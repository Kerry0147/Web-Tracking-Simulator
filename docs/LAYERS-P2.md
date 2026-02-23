# Project ECHO — Phase 2 Build Layers
## Layered Code Generation Roadmap for Claude Code (AI Integration)

### How to Use This File
1. **Prerequisite:** Phase 1 (Layers 1–7) must be fully deployed and passing all tests
2. Work through layers **in order** (P2-Layer 1 → 2 → 3)
3. For each layer, paste the **Claude Code Prompt** into your Claude Code session in VS Code
4. **Test** using the verification steps before moving to the next layer
5. If a layer fails testing, fix it before proceeding

### Phase Toggle: `AI_MODE`
Phase 2 introduces an `AI_MODE` environment variable that controls whether the system uses Phase 1 hardcoded rules or Phase 2 LLM-powered intelligence. This variable is the **single switch** between phases.

| `AI_MODE` | Classification | Chat | Insight Text |
|-----------|---------------|------|-------------|
| `phase1` (default) | Rule engine | Keyword matching | `<Hard Code>` prefixed |
| `phase2` | Claude Haiku 4.5 API | Claude with tool use | AI-generated natural language |

**Safety:** When `AI_MODE=phase2`, any LLM failure automatically falls back to Phase 1 behavior for that call. The demo never breaks.

### Phase 1 ↔ Phase 2 File Relationship

| Phase 2 File | Action | Phase 1 File It Connects To | Relationship |
|-------------|--------|----------------------------|-------------|
| `app/config.py` | **NEW** | `.env` | Reads AI_MODE + API key; consumed by all Phase 2 modules |
| `app/engine/llm_client.py` | **NEW** | `app/engine/classifier.py` + `app/engine/nba_engine.py` | Replaces both when AI_MODE=phase2; calls Claude API instead of rule engine |
| `app/skills/routing_skills.py` | **MODIFY** | (self — Phase 1 version) | Adds AI_MODE check; routes to `llm_client.py` or original `classifier.py`/`nba_engine.py` |
| `app/chat/handler.py` | **MODIFY** | (self — Phase 1 version) | Adds AI_MODE check; routes to Claude chat or original keyword handler |
| `requirements.txt` | **MODIFY** | (self — Phase 1 version) | Adds `anthropic` SDK |
| `.env` | **MODIFY** | (self — Phase 1 version) | Adds `AI_MODE=phase1` line |

### Files NOT Modified in Phase 2 (Preserved from Phase 1)

These files remain exactly as deployed in Phase 1 Layers 1–7:

```
app/models.py                          # Enums + Pydantic models (the shared contract)
app/data/mock_data.json                # Mock dataset
app/engine/behavior_tracker.py         # Event processing + point accumulation
app/engine/session_manager.py          # Session lifecycle
app/engine/stream_manager.py           # SSE broadcast
app/engine/classifier.py               # KEPT as fallback (not deleted)
app/engine/nba_engine.py               # KEPT as fallback (not deleted)
app/skills/read_skills.py              # Mock data retrieval (also used as LLM tools)
app/chat/telegram_bridge.py            # Telegram escalation
app/main.py                            # Routes + SSE pipeline (unchanged)
templates/**                           # All HTML templates
static/**                              # All CSS + JS including behavior.js
```

---

## P2-Layer 1: Config & LLM Client Foundation
**Goal:** Create the configuration module and the core LLM client that can call Claude API and return validated `ClassificationResult` + `NBAResult` objects. No wiring yet — just the standalone module with fallback logic.

### Phase 1 Connection
- **Depends on:** `app/models.py` (Layer 1) — uses `ClassificationResult`, `NBAResult`, all enums
- **Depends on:** `app/engine/classifier.py` (Layer 5) — imports for fallback
- **Depends on:** `app/engine/nba_engine.py` (Layer 5) — imports for fallback
- **Will be consumed by:** `app/skills/routing_skills.py` (P2-Layer 2)

### PRD-P2 Sections to Read
- Section 2 (Phase Toggle: `AI_MODE`)
- Section 3 (LLM Model Selection)
- Section 4 (AI Classification Skill — system prompt, payload, response schema, validation)

### Files to Generate
```
app/
├── config.py                 # NEW: Centralized config (AI_MODE, API key, model)
├── engine/
│   └── llm_client.py         # NEW: Claude API wrapper + JSON parsing + validation
requirements.txt              # MODIFY: Add anthropic SDK
.env                          # MODIFY: Add AI_MODE=phase1
```

### Claude Code Prompt
```
Read docs/PRD-P2.md sections 2 (Phase Toggle), 3 (LLM Model Selection), and 4 (AI Classification Skill).

Also read the existing Phase 1 files for context:
- app/models.py (all Pydantic models and enums — this is the shared contract)
- app/engine/classifier.py (the Phase 1 rule engine — this becomes the fallback)
- app/engine/nba_engine.py (the Phase 1 NBA logic — also fallback)
- app/engine/behavior_tracker.py (understand SessionState structure and what data is available)

Generate P2-Layer 1: Config & LLM Client Foundation.

Create app/config.py:
- Load .env via python-dotenv
- Export: AI_MODE (str, default "phase1"), ANTHROPIC_API_KEY (str), LLM_MODEL (str, "claude-haiku-4-5-20251001"), LLM_TIMEOUT (int, 10), LLM_MAX_TOKENS (int, 1024)
- Simple module — no classes needed

Create app/engine/llm_client.py:
- Import anthropic SDK, app.config, app.models (ClassificationResult, NBAResult, all enums)
- Import the Phase 1 functions for fallback: classify_behavior from classifier.py, determine_nba from nba_engine.py

- Function: build_session_context(session: SessionState, customer_data: Optional[Dict]) -> str
  - Builds a human-readable text summary of the session state for the LLM prompt
  - Include: page visit sequence (from events), page visit counts, dwell times, raw intent points, sentiment signals, rage click count, event count
  - If customer_data exists: include customer name, tier, LTV, open cases (id + subject + status), historical sessions (intent + sentiment per session)
  - Format as structured text sections, NOT raw JSON dumps

- Function: async llm_classify_behavior(session: SessionState, customer_data: Optional[Dict]) -> tuple[ClassificationResult, NBAResult]
  - Build context string via build_session_context()
  - Construct messages: system prompt (per PRD-P2 Section 4.3) + user message with context
  - Call Anthropic API using the anthropic Python SDK (async client)
  - Parse JSON response
  - Validate all enum values are valid members of their respective enums
  - Validate intent_scores keys are valid Intent enums and percentages sum to ~100
  - Convert to ClassificationResult and NBAResult objects
  - Return the tuple

- Fallback wrapper: async safe_llm_classify(session, customer_data) -> tuple[ClassificationResult, NBAResult]
  - Try llm_classify_behavior()
  - On ANY exception (API error, timeout, invalid JSON, validation failure):
    - Log: print(f"⚠️ LLM fallback: using Phase 1 rules (reason: {error})")
    - Call Phase 1: classify_behavior(session, customer_data) and determine_nba(result)
    - Return the Phase 1 result

- Debounce tracking: module-level dict _last_call_times: Dict[str, float] = {}
  - Function: should_call_llm(session_id: str) -> bool
    - Returns True if last call was >2 seconds ago OR if session has rage_click events since last call
    - Updates timestamp on call

UPDATE requirements.txt:
- Add: anthropic

UPDATE .env:
- Add line: AI_MODE=phase1
- Keep existing TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, ANTHROPIC_API_KEY lines unchanged
```

### Test
```bash
# Test 1: Config loads correctly
python -c "
from app.config import AI_MODE, ANTHROPIC_API_KEY, LLM_MODEL, LLM_TIMEOUT
print(f'AI_MODE: {AI_MODE}')
print(f'Model: {LLM_MODEL}')
print(f'Timeout: {LLM_TIMEOUT}')
print(f'API Key set: {bool(ANTHROPIC_API_KEY)}')
print('Config OK')
"

# Test 2: Context builder works with mock session
python -c "
import time
from app.models import SessionState, BehaviorEvent, Intent, Sentiment
from app.engine.llm_client import build_session_context

session = SessionState(
    session_id='test-001',
    start_time=time.time(),
    events=[
        BehaviorEvent(type='page_view', page='/troubleshooting', timestamp=time.time()),
        BehaviorEvent(type='page_view', page='/troubleshooting/monitor', timestamp=time.time()),
    ],
    page_visits={'/troubleshooting': 1, '/troubleshooting/monitor': 1},
    raw_intent_points={Intent.TROUBLESHOOTING: 35.0, Intent.GENERAL_BROWSING: 6.0},
    sentiment_signals={s: 0 for s in Sentiment}
)

context = build_session_context(session, None)
print(context)
print('---')
assert 'TROUBLESHOOTING' in context
assert 'page' in context.lower()
print('Context builder OK')
"

# Test 3: Fallback works when API key is missing/invalid
python -c "
import asyncio
from app.engine.llm_client import safe_llm_classify
from app.models import SessionState, Intent, Sentiment
import time

session = SessionState(
    session_id='test-fallback',
    start_time=time.time(),
    raw_intent_points={Intent.TROUBLESHOOTING: 55.0, Intent.GENERAL_BROWSING: 12.0},
    sentiment_signals={s: 0 for s in Sentiment}
)

classification, nba = asyncio.run(safe_llm_classify(session, None))
print(f'Segment: {classification.segment.value}')
print(f'Intent: {classification.primary_intent.value}')
print(f'NBA: {nba.state.value}')
print(f'Insight prefix: {classification.insights[\"segment\"][:12]}')
assert '<Hard Code>' in classification.insights['segment']  # Fallback should produce hardcoded
print('Fallback OK — Phase 1 rules used when API unavailable')
"
```

### Done When
- [ ] `app/config.py` loads AI_MODE correctly from `.env` (defaults to `phase1`)
- [ ] `build_session_context()` produces readable text from SessionState
- [ ] `llm_classify_behavior()` calls Claude API and returns valid `ClassificationResult` + `NBAResult` (when API key is valid)
- [ ] `safe_llm_classify()` falls back to Phase 1 rule engine on any LLM failure
- [ ] Debounce logic (`should_call_llm`) prevents excessive API calls
- [ ] `requirements.txt` includes `anthropic`
- [ ] `.env` includes `AI_MODE=phase1` line
- [ ] Phase 1 behavior is completely unchanged (no imports broken, no side effects)

---

## P2-Layer 2: Classification Swap & Chat AI
**Goal:** Wire the LLM client into the existing pipeline by modifying `routing_skills.py` (for classification) and `chat/handler.py` (for chat). After this layer, setting `AI_MODE=phase2` in `.env` activates full AI behavior.

### Phase 1 Connection
- **Modifies:** `app/skills/routing_skills.py` (Layer 5) — adds AI_MODE branch in `execute_classification()`
- **Modifies:** `app/chat/handler.py` (Layer 7) — adds AI_MODE branch in `handle_message()`
- **Depends on:** `app/engine/llm_client.py` (P2-Layer 1) — the LLM classification function
- **Depends on:** `app/config.py` (P2-Layer 1) — AI_MODE toggle
- **Depends on:** `app/skills/read_skills.py` (Layer 5) — read skills become Claude chat tools
- **Consumed by:** `app/main.py` (Layer 2→7) — no changes needed; main.py already calls `router.execute_classification()` and `handle_message()`

### PRD-P2 Sections to Read
- Section 2.3–2.4 (Toggle Behavior and Automatic Fallback)
- Section 5 (AI Chat Skill — tool use, system prompt, escalation detection)
- Section 6 (Integration Points — routing skills update, data flow)

### Files to Modify
```
app/
├── skills/
│   └── routing_skills.py     # MODIFY: Add AI_MODE toggle in execute_classification()
├── chat/
│   └── handler.py            # MODIFY: Add AI_MODE toggle + Claude chat with tool use
```

### Claude Code Prompt
```
Read docs/PRD-P2.md sections 2.3-2.4 (Toggle Behavior), 5 (AI Chat Skill), and 6 (Integration Points).

Also read the existing Phase 1 files being modified:
- app/skills/routing_skills.py (current orchestration — this is what we're adding the toggle to)
- app/chat/handler.py (current keyword handler — this gets an LLM branch)
- app/skills/read_skills.py (these become tools for the chat LLM)
- app/main.py (understand how routing_skills and handler are called — we do NOT modify main.py)

And the new Phase 2 files from P2-Layer 1:
- app/config.py (AI_MODE variable)
- app/engine/llm_client.py (safe_llm_classify function)

Generate P2-Layer 2: Classification Swap & Chat AI.

MODIFY app/skills/routing_skills.py:
- Import AI_MODE from app.config
- Import safe_llm_classify from app.engine.llm_client
- Import should_call_llm from app.engine.llm_client
- Keep ALL existing Phase 1 imports (classifier.py, nba_engine.py, read_skills.py)

- In execute_classification():
  - Keep existing customer_context loading logic UNCHANGED
  - Add branch:
    if AI_MODE == "phase2" and should_call_llm(session.session_id):
        # Use LLM (with automatic fallback built into safe_llm_classify)
        classification, nba = await safe_llm_classify(session, customer_context)
    else:
        # Phase 1 original logic (unchanged)
        classification = classify_behavior(session, customer_context)
        nba = determine_nba(classification)
  
  - IMPORTANT: execute_classification must become async (add async def)
  - The return type stays the same: tuple[ClassificationResult, NBAResult]
  
  - Add a module-level cache: _last_result: Dict[str, tuple] = {}
    - When should_call_llm returns False, return cached result for that session
    - Update cache after every fresh classification

- CRITICAL: The function signature change (sync → async) means callers need await.
  Check app/main.py — it calls router.execute_classification() in:
    1. common_context() — called synchronously from route handlers
    2. render_dashboard_partials() — called from sync context
    3. track_event() — called from async handler
  
  To handle this WITHOUT modifying main.py: use asyncio.run() or make execute_classification
  detect if it's being called from async context. 
  
  PREFERRED APPROACH: Keep execute_classification synchronous. Inside it, when AI_MODE=phase2,
  use asyncio.get_event_loop().run_until_complete() or import asyncio and run the coroutine.
  This preserves the Phase 1 calling convention in main.py.
  
  Alternative: use the synchronous Anthropic client (anthropic.Anthropic instead of 
  anthropic.AsyncAnthropic) so no async is needed at all. This is simpler and recommended.

MODIFY app/chat/handler.py:
- Import AI_MODE from app.config
- Import anthropic SDK
- Import config values (ANTHROPIC_API_KEY, LLM_MODEL, LLM_TIMEOUT, LLM_MAX_TOKENS)
- Import read_skills functions (get_customer_profile, check_warranty_status, get_customer_history)
- Keep the ENTIRE existing handle_message function as-is, renamed to _phase1_handle_message

- Create new handle_message(message, session_state, customer_data) function:
  - If AI_MODE != "phase2": return _phase1_handle_message(message, session_state, customer_data)
  - If AI_MODE == "phase2":
    try:
      return _llm_handle_message(message, session_state, customer_data)
    except Exception as e:
      print(f"⚠️ Chat LLM fallback: {e}")
      return _phase1_handle_message(message, session_state, customer_data)

- Create _llm_handle_message(message, session_state, customer_data) function:
  - Build system prompt per PRD-P2 Section 5.3
  - Include customer context in system prompt if customer_data exists:
    - Customer name, tier, LTV
    - Devices and warranty status
    - Open cases
    - Current session sentiment and intent
  - Define tools array for Claude tool use:
    - get_customer_profile: input schema { customer_id: string }
    - check_warranty_status: input schema { identifier: string, is_serial: boolean }
    - get_customer_history: input schema { customer_id: string }
  - Call Anthropic API with messages + tools
  - Handle tool_use responses: execute the matching read_skill function with mock_data, 
    return tool result, continue conversation
  - Parse final text response as JSON { reply, escalation_required }
  - Return the dict

  IMPORTANT: The read_skills functions need mock_data as a parameter. To access it:
  - Import mock_db from app.main (it's a module-level dict populated at startup)
  - OR pass mock_data through the function chain
  - Simplest: import mock_db from app.main at function call time (lazy import to avoid circular)

Do NOT modify any other files. app/main.py, templates, static files, and all other engine files remain unchanged.
```

### Test
```bash
# === Test Group A: Phase 1 Still Works ===

# Ensure .env has AI_MODE=phase1
# Start server: uvicorn app.main:app --reload --port 8000

# Test A1: Full Phase 1 demo walkthrough should be identical to pre-Phase-2
# - Open app, browse, login as Sarah, check dashboard updates
# - All <Hard Code> prefixes should still appear
# - Verify: No regressions from Phase 2 code changes

# === Test Group B: Phase 2 Active ===

# Change .env to AI_MODE=phase2 (with valid ANTHROPIC_API_KEY)
# Restart server: uvicorn app.main:app --reload --port 8000

# Test B1: Classification works
# - Open app → browse to Troubleshooting → Monitor → KB article
# - Right pane should update with AI-generated insights (no <Hard Code> prefix)
# - Sentiment and Intent should be contextually appropriate

# Test B2: Login enriches AI context
# - Login as Sarah → dashboard should show AI-generated segment insight
# - Insight should reference her open case or recurring issue

# Test B3: Chat works
# - Open chat → type "My monitor keeps flickering"
# - Response should be contextual (not the hardcoded keyword match)
# - Response should NOT have <Hard Code> prefix

# Test B4: Chat escalation
# - Type "I want to talk to a real person"
# - Should trigger escalation (Telegram notification fires)

# Test B5: Fallback resilience
# - Set ANTHROPIC_API_KEY to an invalid value in .env
# - Restart server
# - Browse the app — dashboard should still update (with <Hard Code> prefixed fallback)
# - Console should show: "⚠️ LLM fallback: using Phase 1 rules (reason: ...)"

# === Test Group C: Toggle Switch ===

# Test C1: Mid-session switch
# - Start with AI_MODE=phase2 (valid key), browse around, verify AI insights
# - Stop server, change .env to AI_MODE=phase1, restart
# - Continue browsing — verify <Hard Code> prefixes return
# - This confirms the toggle works as a reliable demo safety net
```

### Done When
- [ ] `AI_MODE=phase1` → app behaves identically to pre-Phase-2 (no regressions)
- [ ] `AI_MODE=phase2` → classification returns AI-generated insights without `<Hard Code>` prefix
- [ ] `AI_MODE=phase2` → NBA transitions (Passive → Opportunity → Critical) work correctly
- [ ] `AI_MODE=phase2` → chat responses are contextual and reference customer data
- [ ] `AI_MODE=phase2` → chat escalation detected by Claude (not just keyword matching)
- [ ] LLM failure → automatic fallback to Phase 1 with console warning
- [ ] Debounce prevents excessive API calls during rapid navigation
- [ ] `app/main.py` is NOT modified — routing_skills handles the toggle internally
- [ ] `app/engine/classifier.py` is NOT modified — preserved as fallback
- [ ] `app/engine/nba_engine.py` is NOT modified — preserved as fallback

---

## Final Integration Test (Phase 2)

After both layers are complete, run through the **full Demo Walkthrough Script** (Phase 1 PRD Section 8) twice:

### Run 1: AI_MODE=phase2

| Scene | Duration | Phase 2 Specific Validation |
|-------|----------|---------------------------|
| 1. Anonymous Visitor | 2 min | AI insights should describe browsing patterns naturally (no `<Hard Code>`) |
| 2. Login & Profile Merge | 1 min | AI should reference Sarah's open case and recurring visits in segment insight |
| 3. Logged-In Auto-Population | 1 min | Pages unchanged — this tests Phase 1 UI is intact |
| 4. Deepening Concern | 2 min | AI sentiment insight should mention page revisit pattern specifically |
| 5. Frustration & Critical NBA | 1 min | AI NBA text should be contextual ("recurring monitor issue, expired warranty") |
| 6. Chat & Escalation | 1 min | Chat should use Claude — contextual replies, tool use for data lookup |

### Run 2: AI_MODE=phase1 (Regression Check)

Repeat the same walkthrough. **Everything should be identical to the original Phase 1 deployment.** All `<Hard Code>` prefixes present. No errors in console.

### Toggle Test

During a live demo:
1. Start with `AI_MODE=phase2`
2. If any LLM issue occurs, stop server, change `.env` to `AI_MODE=phase1`, restart
3. Demo continues seamlessly with hardcoded behavior

**Phase 2 is complete when both runs pass and the toggle switch works reliably.** ✅

---

## Quick Reference: Phase 2 File Map

| File | Layer | Status | Purpose |
|------|-------|--------|---------|
| `app/config.py` | P2-L1 | NEW | AI_MODE toggle + API config |
| `app/engine/llm_client.py` | P2-L1 | NEW | Claude API wrapper + validation + fallback |
| `requirements.txt` | P2-L1 | MODIFIED | Add `anthropic` SDK |
| `.env` | P2-L1 | MODIFIED | Add `AI_MODE=phase1` |
| `app/skills/routing_skills.py` | P2-L2 | MODIFIED | Toggle between LLM and rule engine |
| `app/chat/handler.py` | P2-L2 | MODIFIED | Toggle between LLM chat and keyword handler |
