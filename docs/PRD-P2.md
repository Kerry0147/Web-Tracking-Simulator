# Project ECHO — PRD Phase 2 (AI-Powered Classification & Chat)
## LLM Replacement for Hardcoded Outputs

| Field | Value |
|-------|-------|
| Version | 2.0 (Phase 2 — AI Integration) |
| Date | February 12, 2026 |
| Status | Ready for Code Generation |
| Phase | Phase 2 — Replace all `<Hard Code>` markers with Claude API calls |
| Prerequisite | Phase 1 fully deployed and tested (Layers 1–7) |
| LLM Provider | Anthropic (Claude Haiku 4.5) |
| Model String | `claude-haiku-4-5-20251001` |

---

## 1. Phase 2 Objective

Replace every `<Hard Code>` prefixed output in Phase 1 with real-time Claude API calls while preserving the exact same data contracts, SSE pipeline, and UI. The Phase 1 rule engine (`classifier.py` + `nba_engine.py`) and hardcoded chat handler (`chat/handler.py`) become AI-powered — Claude reads raw behavioral events and returns structured JSON using the same enums and models.

### 1.1 What Changes

| Component | Phase 1 (Current) | Phase 2 (Target) |
|-----------|-------------------|-------------------|
| `classifier.py` | Rule-based thresholds (PRD Section 4) | Claude API call with structured JSON response |
| `nba_engine.py` | If/else logic on classification output | Claude determines NBA state as part of classification |
| `chat/handler.py` | Keyword-matching hardcoded replies | Claude with tool use (read skills) for conversational responses |
| Insight text (all sections) | Static `<Hard Code>` strings | Claude-generated natural language explanations |

### 1.2 What Does NOT Change

Everything else from Phase 1 remains untouched:

- `app/models.py` — All Pydantic models and enums (Segment, Intent, Sentiment, NBAState)
- `app/data/mock_data.json` — Complete mock dataset
- `app/engine/behavior_tracker.py` — Client-side event processing and point accumulation
- `app/engine/session_manager.py` — Session lifecycle management
- `app/engine/stream_manager.py` — SSE broadcast infrastructure
- `app/skills/read_skills.py` — Mock data retrieval functions
- `app/chat/telegram_bridge.py` — Telegram escalation (unchanged)
- All templates (`templates/**`) — HTML partials, layout, components
- All static files (`static/**`) — CSS, JS including `behavior.js`
- `app/main.py` — Route structure, SSE endpoints, tracking pipeline (minimal update only)

---

## 2. Phase Toggle: `AI_MODE` Environment Variable

### 2.1 Design Principle

Phase 2 must **never break the demo**. If the LLM API is unavailable, slow, or returns invalid data, the system must silently fall back to Phase 1 hardcoded behavior. This is controlled by a single environment variable.

### 2.2 Configuration

**`.env` file:**
```
# Phase Toggle
AI_MODE=phase1              # "phase1" = hardcoded rules (default), "phase2" = Claude API

# Claude API (required when AI_MODE=phase2)
ANTHROPIC_API_KEY=sk-ant-...

# Existing (unchanged)
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

### 2.3 Toggle Behavior

| `AI_MODE` Value | Classification | Chat | Insight Text |
|-----------------|---------------|------|-------------|
| `phase1` (default) | Rule engine (`classifier.py` original logic) | Keyword-matching hardcoded replies | Static `<Hard Code>` strings |
| `phase2` | Claude API call → structured JSON | Claude with tool use | Claude-generated natural language |

### 2.4 Automatic Fallback (Safety Net)

When `AI_MODE=phase2`, every LLM call is wrapped in a try/except. On **any** failure — timeout, API error, invalid JSON, missing API key — the system automatically falls back to the Phase 1 rule engine for that specific call. This means:

- A single failed API call does not crash the demo
- The dashboard continues updating (with hardcoded output for that one cycle)
- The next event triggers a fresh API attempt
- Console logs indicate when fallback is activated: `⚠️ LLM fallback: using Phase 1 rules (reason: ...)`

### 2.5 Config Module

**New file: `app/config.py`**

```python
import os
from dotenv import load_dotenv

load_dotenv()

AI_MODE = os.getenv("AI_MODE", "phase1")          # Default: safe hardcoded mode
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL = "claude-haiku-4-5-20251001"
LLM_TIMEOUT = 10                                    # seconds — fail fast for SSE responsiveness
LLM_MAX_TOKENS = 1024
```

---

## 3. LLM Model Selection

### 3.1 Recommended Model: Claude Haiku 4.5

| Criteria | Why Haiku 4.5 |
|----------|---------------|
| Task fit | Structured JSON classification from behavioral signals — moderate complexity, well within Haiku's range |
| Latency | Sub-1-second response for short prompts — critical for real-time SSE dashboard updates |
| Cost | ~10-25x cheaper than Opus per token — sustainable for PoC with hundreds of calls per demo session |
| Reliability | Strong at following structured output schemas with enum constraints |

### 3.2 Upgrade Path

If Haiku occasionally misclassifies edge cases (e.g., CAUTIOUS vs. CONFUSED distinction), swap `LLM_MODEL` in `config.py` to `claude-sonnet-4-5-20250929` — no other code changes required.

---

## 4. AI Classification Skill (`classify_behavior` — Phase 2)

### 4.1 What It Replaces

This replaces the **entire** Phase 1 rule engine:

| Phase 1 File | Phase 1 Function | Phase 2 Replacement |
|-------------|-----------------|---------------------|
| `app/engine/classifier.py` | `classify_behavior()` | `llm_classify_behavior()` in new `app/engine/llm_client.py` |
| `app/engine/nba_engine.py` | `determine_nba()` | Merged into LLM classification (Claude returns NBA as part of response) |

### 4.2 Input: Session Context Payload

The LLM receives a structured text summary of the current session state. This is built from the same `SessionState` and `customer_data` objects that the Phase 1 rule engine consumed.

**Payload fields sent to Claude:**

| Field | Source | Example |
|-------|--------|---------|
| Page visit sequence | `session.events` (filtered to page_view) | `["/", "/troubleshooting", "/troubleshooting/monitor", "/troubleshooting/monitor/KB-MON-002"]` |
| Page visit counts | `session.page_visits` | `{"/troubleshooting/monitor/KB-MON-002": 3}` |
| Dwell times | `session.accumulated_dwell` | `{"/troubleshooting/monitor/KB-MON-002": 260.0}` |
| Raw intent points | `session.raw_intent_points` | `{TROUBLESHOOTING: 55, GENERAL_BROWSING: 12}` |
| Sentiment signals | `session.sentiment_signals` | `{FRUSTRATED: 40, CONFUSED: 20}` |
| Event count | `len(session.events)` | `14` |
| Rage click count | Count of `rage_click` events | `2` |
| Customer profile | `customer_data.profile.customer` (if logged in) | `{name: "Sarah Chen", tier: "Gold", ltv: 3249.97}` |
| Open cases | `customer_data.history.cases` (if logged in) | `[{id: "CASE-2026-0891", status: "Open", subject: "Monitor flickering returned"}]` |
| Historical sessions | `customer_data.history.sessions` (if logged in) | `[{intent: "TROUBLESHOOTING", sentiment: "FRUSTRATED"}, ...]` |

### 4.3 System Prompt

```
You are the AI classification engine for a Customer Engagement Center. Analyze the customer's behavioral signals and return a JSON classification.

RULES:
- You MUST use ONLY these enum values (no others):
  - Segment: NEW_VISITOR, RETURNING, VIP, AT_RISK, DORMANT
  - Intent: GENERAL_BROWSING, TROUBLESHOOTING, WARRANTY_INQUIRY, PURCHASE_SIGNAL, CASE_FOLLOW_UP
  - Sentiment: NEUTRAL, POSITIVE, CONFUSED, CAUTIOUS, FRUSTRATED
  - NBA State: PASSIVE, OPPORTUNITY, CRITICAL

- Segment priority: AT_RISK > VIP > DORMANT > RETURNING > NEW_VISITOR
- NBA logic: CRITICAL if sentiment is FRUSTRATED or (segment is AT_RISK and troubleshooting intent > 50%). OPPORTUNITY if troubleshooting intent > 60% and sentiment is not FRUSTRATED. Otherwise PASSIVE.
- should_trigger_chat: true ONLY when NBA is CRITICAL

- Intent scores must be normalized percentages summing to 100.
- Insights should be 1-2 sentences, professional and measured (not alarmist).
- Do NOT prefix insights with "<Hard Code>".

Respond with ONLY valid JSON matching this exact schema:
{
  "segment": "<enum>",
  "primary_intent": "<enum>",
  "intent_scores": {"TROUBLESHOOTING": 72.1, "WARRANTY_INQUIRY": 18.0, ...},
  "sentiment": "<enum>",
  "nba_state": "<PASSIVE|OPPORTUNITY|CRITICAL>",
  "nba_action_text": "<1-2 sentence recommendation>",
  "should_trigger_chat": false,
  "insights": {
    "segment": "<1-2 sentence explanation>",
    "intent": "<1-2 sentence explanation>",
    "sentiment": "<1-2 sentence explanation>"
  }
}
```

### 4.4 Expected Response Schema

The LLM JSON response maps directly to the existing Phase 1 data contracts:

| JSON Field | Maps To | Pydantic Model |
|-----------|---------|---------------|
| `segment` | `ClassificationResult.segment` | `Segment` enum |
| `primary_intent` | `ClassificationResult.primary_intent` | `Intent` enum |
| `intent_scores` | `ClassificationResult.intent_scores` | `Dict[Intent, float]` |
| `sentiment` | `ClassificationResult.sentiment` | `Sentiment` enum |
| `nba_state` | `NBAResult.state` | `NBAState` enum |
| `nba_action_text` | `NBAResult.action_text` | `str` |
| `should_trigger_chat` | `NBAResult.should_trigger_chat` | `bool` |
| `insights.segment` | `ClassificationResult.insights["segment"]` | `str` |
| `insights.intent` | `ClassificationResult.insights["intent"]` | `str` |
| `insights.sentiment` | `ClassificationResult.insights["sentiment"]` | `str` |

### 4.5 Validation

After parsing the LLM JSON response, the system must validate:

1. All enum values are valid members of their respective enums
2. `intent_scores` keys are valid `Intent` enum values and sum to ~100%
3. `nba_state` is a valid `NBAState` value
4. `should_trigger_chat` is a boolean
5. All three insight strings are non-empty

If any validation fails → fallback to Phase 1 rule engine for this call.

---

## 5. AI Chat Skill (Phase 2)

### 5.1 What It Replaces

| Phase 1 File | Phase 1 Function | Phase 2 Replacement |
|-------------|-----------------|---------------------|
| `app/chat/handler.py` | `handle_message()` — keyword matching | `llm_handle_message()` in updated `app/chat/handler.py` |

### 5.2 Claude Tool Use (Read Skills as Tools)

In Phase 2, the chat agent uses Claude's tool use capability. The read skills from Phase 1 (`read_skills.py`) become tools the LLM can call.

**Tools provided to Claude:**

| Tool Name | Maps To | Description |
|-----------|---------|-------------|
| `get_customer_profile` | `read_skills.get_customer_profile()` | Returns customer name, tier, LTV, registered devices |
| `check_warranty_status` | `read_skills.check_warranty_status()` | Returns warranty records for customer or specific serial number |
| `get_customer_history` | `read_skills.get_customer_history()` | Returns historical sessions and support cases |

### 5.3 Chat System Prompt

```
You are the ProBook AI Assistant, a helpful customer support agent for ProBook Electronics (laptops and tablets).

CONTEXT PROVIDED:
- Customer profile (if logged in): name, tier, devices, warranty status
- Current session: pages visited, behavioral analysis, sentiment
- Support history: past cases, interaction logs

RULES:
- Be helpful, concise, and professional
- Reference specific customer data when relevant (e.g., "I can see your GX-7500's warranty expired on...")
- If the customer mentions wanting a human agent, set escalation_required to true
- Do NOT prefix responses with "<Hard Code>"
- Keep responses under 3 sentences unless the customer asks for detail
- You have access to tools to look up customer data — use them when relevant

Respond with JSON:
{
  "reply": "<your response text>",
  "escalation_required": false
}
```

### 5.4 Escalation Detection

The LLM handles escalation detection naturally through conversation understanding, replacing the Phase 1 keyword list (`["agent", "human", "person", "representative", "transfer"]`). Claude recognizes intent to escalate even with indirect phrasing like "I give up" or "this isn't working, I need someone."

If the LLM sets `escalation_required: true`, the existing Telegram bridge (`telegram_bridge.py`) fires exactly as in Phase 1 — no changes needed.

### 5.5 Fallback

When `AI_MODE=phase2` and the chat LLM call fails, fall back to the Phase 1 keyword-matching handler. The user sees a `<Hard Code>` prefixed response (acceptable degradation during a demo).

---

## 6. Integration Points with Phase 1

### 6.1 Routing Skills Update

**File: `app/skills/routing_skills.py`**

This is the **primary integration point**. The `execute_classification()` method currently calls:
1. `classify_behavior()` from `classifier.py`
2. `determine_nba()` from `nba_engine.py`

In Phase 2, when `AI_MODE=phase2`, it instead calls:
1. `llm_classify_behavior()` from `llm_client.py` — which returns **both** classification and NBA in one LLM call

The return types remain identical: `tuple[ClassificationResult, NBAResult]`.

### 6.2 Data Flow (Phase 2)

```
Browser (behavior.js) → POST /api/track-event → behavior_tracker.py (UNCHANGED)
    ↓
routing_skills.py checks AI_MODE
    ↓
[phase1] → classifier.py → nba_engine.py → ClassificationResult + NBAResult
[phase2] → llm_client.py (Claude API) → ClassificationResult + NBAResult
    ↓
render_dashboard_partials() → SSE push (UNCHANGED)
```

### 6.3 File Dependency Map

New and modified files in Phase 2, with their Phase 1 dependencies:

| File | Status | Depends On (Phase 1) | Purpose |
|------|--------|---------------------|---------|
| `app/config.py` | **NEW** | `.env` | Centralized config: AI_MODE, API key, model |
| `app/engine/llm_client.py` | **NEW** | `app/models.py`, `app/config.py` | Claude API wrapper + JSON parsing + validation |
| `app/skills/routing_skills.py` | **MODIFIED** | `llm_client.py`, `classifier.py`, `nba_engine.py` | Toggle between Phase 1 and Phase 2 classification |
| `app/chat/handler.py` | **MODIFIED** | `llm_client.py`, `read_skills.py` | Toggle between hardcoded and LLM chat |
| `requirements.txt` | **MODIFIED** | — | Add `anthropic` SDK |
| `.env` | **MODIFIED** | — | Add `AI_MODE` variable |

### 6.4 Unchanged Files (Explicit Confirmation)

These files are **not modified** in Phase 2:

- `app/models.py` — Enums and Pydantic models are the contract; both phases use them identically
- `app/engine/behavior_tracker.py` — Raw event processing and point accumulation stays rule-based (this feeds *input* to the LLM, it doesn't need replacing)
- `app/engine/session_manager.py` — Session lifecycle unchanged
- `app/engine/stream_manager.py` — SSE infrastructure unchanged
- `app/engine/classifier.py` — **Preserved as-is** for Phase 1 fallback (not deleted)
- `app/engine/nba_engine.py` — **Preserved as-is** for Phase 1 fallback (not deleted)
- `app/skills/read_skills.py` — Mock data retrieval unchanged (also used as chat tools)
- `app/chat/telegram_bridge.py` — Telegram escalation unchanged
- `app/main.py` — Routes and SSE pipeline unchanged (routing_skills handles the toggle internally)
- All templates and static files — Unchanged

---

## 7. Performance Considerations

### 7.1 Latency Budget

The SSE dashboard must feel real-time. Phase 2 introduces an LLM API call in the critical path.

| Component | Phase 1 Latency | Phase 2 Latency Target |
|-----------|----------------|----------------------|
| Event tracking + rule engine | ~5ms | ~5ms (unchanged) |
| LLM classification call | N/A | < 1,000ms (Haiku target) |
| SSE push + render | ~10ms | ~10ms (unchanged) |
| **Total per event** | **~15ms** | **< 1,100ms** |

### 7.2 Optimization: Skip Redundant Calls

Not every tracked event needs a fresh LLM call. Implement a debounce:

- **Minimum interval:** 2 seconds between LLM classification calls
- **Between calls:** Use the most recent cached `ClassificationResult` and `NBAResult`
- **Always call on:** Login event, rage_click event, first page_view of session

This reduces API costs and keeps the dashboard responsive during rapid navigation.

### 7.3 Token Budget Per Call

| Component | Estimated Tokens |
|-----------|-----------------|
| System prompt | ~400 |
| Session context payload | ~200–500 (varies with event count) |
| Response | ~200–300 |
| **Total per call** | **~800–1,200 tokens** |

At Haiku pricing, this is extremely cost-effective for a PoC.

---

## 8. Definition of Done (Phase 2)

### 8.1 Toggle Mechanism
- [ ] `AI_MODE=phase1` produces identical behavior to pre-Phase-2 deployment
- [ ] `AI_MODE=phase2` produces LLM-powered classification and chat
- [ ] Switching `AI_MODE` requires only `.env` change + server restart
- [ ] API failure triggers automatic fallback with console warning

### 8.2 Classification
- [ ] LLM returns valid JSON matching `ClassificationResult` + `NBAResult` schemas
- [ ] All enum values are validated before use
- [ ] Insight text is natural language (no `<Hard Code>` prefix)
- [ ] NBA transitions (Passive → Opportunity → Critical) work correctly
- [ ] Dashboard SSE updates feel responsive (< 1.5s end-to-end)

### 8.3 Chat
- [ ] LLM chat responses reference customer data when relevant
- [ ] Tool use (read skills) works — Claude can look up warranty, profile, history
- [ ] Escalation detection works for both direct ("transfer me") and indirect ("I give up") requests
- [ ] Telegram escalation fires correctly from LLM-detected escalation
- [ ] Chat fallback to Phase 1 on LLM failure

### 8.4 Demo Readiness
- [ ] Full Phase 1 demo walkthrough (PRD Section 8) works identically with `AI_MODE=phase2`
- [ ] Insight text is noticeably better — contextual, specific, not generic
- [ ] Can switch to `phase1` mid-demo if LLM issues arise (restart server with changed `.env`)
- [ ] No `<Hard Code>` prefixes visible when running in Phase 2 mode
