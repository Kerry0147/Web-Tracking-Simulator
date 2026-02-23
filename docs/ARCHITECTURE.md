# Project ECHO — Backend Architecture

## System Overview

```
+---------------------------+          +----------------------------------+
|     BROWSER (Left Pane)   |          |     BROWSER (Right Pane)         |
|     Customer Portal       |          |     Agent Dashboard              |
|                           |          |                                  |
|  behavior.js              |          |  SSE Listener (EventSource)      |
|   - page_view             |          |   - nba-update                   |
|   - click / rage_click    |          |   - vitals-update                |
|   - page_leave + dwell    |          |   - categorization-update        |
|   - form_submit           |          |   - timeline-update              |
|                           |          |   - history-update               |
|  chat.js                  |          |                                  |
|   - sendMessage()         |          |  AI Mode Toggle (JS)             |
|   - escalateChat()        |          |   - toggleAIMode()               |
|   - startPolling()        |          |                                  |
+-----------|---------------+          +-----------------|----------------+
            |                                            ^
            | POST /api/track-event                      | SSE /api/dashboard-stream
            | POST /api/chat/send                        |
            | POST /api/chat/escalate                    |
            v                                            |
+============================================================+
|                    FastAPI  (app/main.py)                   |
|                                                            |
|  ensure_session_id() ──> SessionManager (RAM)              |
|  common_context()    ──> ReadSkills + RoutingSkills         |
|  track_event()       ──> Tracker + Router + SSE Push       |
|  chat_send()         ──> ChatHandler                       |
|  chat_escalate()     ──> TelegramBridge (background)       |
|  toggle_mode()       ──> app_config.AI_MODE = "phase2"     |
+============================================================+
       |              |              |              |
       v              v              v              v
+-----------+  +------------+  +-----------+  +------------+
| Session   |  | Behavior   |  | Routing   |  |  Stream    |
| Manager   |  | Tracker    |  | Skills    |  |  Manager   |
|           |  |            |  |           |  |            |
| RAM dict  |  | Intent pts |  | Phase 1/2 |  | SSE queues |
| session_id|  | Sentiment  |  | branching |  | per tab    |
| -> State  |  | signals    |  |           |  |            |
+-----------+  +------------+  +-----+-----+  +------------+
                                     |
                      +--------------+--------------+
                      |                             |
               Phase 1 (Rules)              Phase 2 (Claude AI)
               +-------------+              +-----------------+
               | classifier  |              | llm_client      |
               | .py         |              | .py             |
               | (Segment,   |              | (Claude API     |
               |  Intent,    |   fallback   |  + JSON parse   |
               |  Sentiment) | <----------- |  + validation)  |
               +------+------+              +-----------------+
                      |                             |
               +------+------+              +-------+--------+
               | nba_engine  |              | build_session   |
               | .py         |              | _context()      |
               | (PASSIVE/   |              | (human-readable |
               |  OPPORTUNITY|              |  text for LLM)  |
               |  /CRITICAL) |              +-----------------+
               +-------------+

               +-------------+              +-----------------+
               | read_skills |              | chat/handler    |
               | .py         |              | .py             |
               | (profile,   |              | Phase 1: keyword|
               |  warranty,  |              | Phase 2: Claude |
               |  history)   |              |  + tool use     |
               +-------------+              +--------+--------+
                                                     |
                                            +--------+--------+
                                            | telegram_bridge |
                                            | .py             |
                                            | (send_escalation|
                                            |  check_replies) |
                                            +-----------------+
                                                     |
                                                     v
                                            Telegram Bot API
                                            (IPv4 forced)
```

---

## Module Map

| Module | File | Role |
|--------|------|------|
| **Config** | `app/config.py` | `AI_MODE`, `ANTHROPIC_API_KEY`, `LLM_MODEL`, `LLM_TIMEOUT`, `LLM_MAX_TOKENS` |
| **Models** | `app/models.py` | Enums (`Segment`, `Intent`, `Sentiment`, `NBAState`) + Pydantic models |
| **Main** | `app/main.py` | FastAPI routes, lifespan, SSE, session wiring |
| **Session Mgr** | `app/engine/session_manager.py` | In-memory `Dict[session_id, SessionState]` |
| **Behavior Tracker** | `app/engine/behavior_tracker.py` | Event processing, intent/sentiment scoring |
| **Stream Mgr** | `app/engine/stream_manager.py` | SSE queue management, multi-tab broadcast |
| **Classifier** | `app/engine/classifier.py` | Phase 1 rule engine (segment, intent, sentiment) |
| **NBA Engine** | `app/engine/nba_engine.py` | Phase 1 NBA logic (PASSIVE/OPPORTUNITY/CRITICAL) |
| **LLM Client** | `app/engine/llm_client.py` | Phase 2 Claude API + debounce + fallback |
| **Routing Skills** | `app/skills/routing_skills.py` | Orchestrator: Phase 1/2 branching + caching |
| **Read Skills** | `app/skills/read_skills.py` | Data retrieval from mock_data.json |
| **Chat Handler** | `app/chat/handler.py` | Phase 1 keyword + Phase 2 LLM chat with tool use |
| **Telegram Bridge** | `app/chat/telegram_bridge.py` | Escalation notification + operator reply polling |

---

## API Endpoints

### Tracking & Dashboard

| Method | Path | Trigger | Calls | Returns |
|--------|------|---------|-------|---------|
| POST | `/api/track-event` | `behavior.js` on every page view, click, rage click | `tracker.process_event()` → `router.execute_classification()` → `render_dashboard_partials()` → `stream_manager.broadcast()` | `{"status": "ok"}` |
| GET | `/api/dashboard-stream` | Browser SSE `EventSource` on page load | `stream_manager.connect()` → yields events from queue | SSE stream (5 event types) |

### Chat

| Method | Path | Trigger | Calls | Returns |
|--------|------|---------|-------|---------|
| POST | `/api/chat/send` | User sends chat message | `handle_message()` (Phase 1 or 2) | `{"reply": str, "escalation_required": bool}` |
| POST | `/api/chat/escalate` | User clicks "Connect Now" | `send_escalation()` (background task to Telegram) | `{"status": "escalated"}` |
| GET | `/api/chat/updates` | `chat.js` polls every 3s after escalation | `check_for_replies()` (Telegram getUpdates) | `{"reply": str or null}` |

### AI Mode Toggle

| Method | Path | Trigger | Calls | Returns |
|--------|------|---------|-------|---------|
| POST | `/api/toggle-mode` | Dashboard toggle switch | Sets `app_config.AI_MODE` in memory | `{"mode": str}` |
| GET | `/api/current-mode` | Dashboard init on page load | Reads `app_config.AI_MODE` | `{"mode": str}` |

### Auth

| Method | Path | Trigger | Calls | Returns |
|--------|------|---------|-------|---------|
| POST | `/login` | Login form submit | Validate credentials → set cookie + RAM → SSE broadcast | HX-Redirect to `/` |
| POST | `/logout` | Logout button | Clear session RAM + cookie | HX-Redirect to `/` |

### Content Pages (GET)

| Path | Template |
|------|----------|
| `/` | `left/home.html` |
| `/products/{category}` | `left/product_detail.html` |
| `/troubleshooting` | `left/troubleshooting.html` |
| `/troubleshooting/{category}` | `left/troubleshooting_list.html` |
| `/troubleshooting/{category}/{article_id}` | `left/kb_article.html` |
| `/warranty` | `left/warranty.html` |
| `/case-status` | `left/case_status.html` |

---

## Data Flow: One Page Click

```
1. User clicks "Troubleshooting" in browser
   |
2. behavior.js sends POST /api/track-event
   { type: "page_view", page: "/troubleshooting", timestamp: 1708... }
   |
3. main.py: track_event()
   |
4. behavior_tracker.process_event(session, event_data)
   +-- Appends BehaviorEvent to session.events[]
   +-- Updates session.page_visits["/troubleshooting"] += 1
   +-- Adds +15 TROUBLESHOOTING intent points
   +-- Adds +3 GENERAL_BROWSING baseline points
   +-- Applies sentiment cooling (-30 FRUSTRATED if was frustrated)
   |
5. routing_skills.execute_classification(session, mock_db)
   |
   +-- Phase 1 path:
   |   classifier.classify_behavior(session, customer_data)
   |     +-- get_normalized_intents() -> {TROUBLESHOOTING: 72%, BROWSING: 28%}
   |     +-- get_current_sentiment() -> NEUTRAL
   |     +-- Segment logic: no customer -> NEW_VISITOR
   |     +-- Generate <Hard Code> insights
   |   nba_engine.determine_nba(classification)
   |     +-- TROUBLESHOOTING 72% > 60% AND NOT FRUSTRATED -> OPPORTUNITY
   |
   +-- Phase 2 path (AI_MODE == "phase2"):
       should_call_llm(session_id, session)
         +-- Check debounce: >2s since last call? Or rage_click?
       safe_llm_classify(session, customer_data)
         +-- build_session_context() -> human-readable text
         +-- Claude API call with system prompt + context
         +-- Parse JSON response, validate enums
         +-- On ANY error: fall back to Phase 1 path
   |
6. render_dashboard_partials(request, session_id, classification, nba)
   +-- Renders 5 Jinja2 templates into HTML strings:
       nba_card.html, vitals.html, categorization.html,
       timeline.html, history.html
   |
7. stream_manager.broadcast_to_session(session_id, ...)
   +-- Pushes 5 SSE events to ALL queues for this session
   +-- Each browser tab receives: { event: "nba-update", data: HTML }
   |
8. Browser SSE listener swaps HTML into DOM via HTMX sse-swap
   +-- Dashboard updates in real-time without page reload
   |
9. Check auto-open: if nba.should_trigger_chat AND !session.chat_triggered:
   +-- Set chat_triggered = True (one-shot)
   +-- Broadcast SSE event: "chat-auto-open"
   +-- Browser opens chat widget automatically
```

---

## Phase 1 vs Phase 2 Branching

```
                        AI_MODE check
                            |
                +-----------+-----------+
                |                       |
           "phase1"                "phase2"
                |                       |
                |                 should_call_llm()?
                |                   |           |
                |                  YES          NO
                |                   |           |
                v                   v           v
        +---------------+   +-----------+  Return cached
        | classifier.py |   | Claude    |  result from
        | (rule engine) |   | API call  |  _last_result{}
        +-------+-------+   +-----+-----+
                |                  |
        +-------+-------+         |
        | nba_engine.py |         |  (Claude returns both
        | (rule matrix) |         |   classification + NBA
        +---------------+         |   in single response)
                |                  |
                v                  v
          ClassificationResult + NBAResult
                |
                v
        render_dashboard_partials()
                |
                v
            SSE push to browser
```

### Fallback Chain

```
Phase 2 LLM call
  |
  +-- Success? -> Return AI result (no <Hard Code> prefix)
  |
  +-- ANY exception (timeout, bad JSON, invalid enum, network error):
      |
      print("[WARNING] LLM fallback: using Phase 1 rules (reason: ...)")
      |
      +-- classify_behavior() -> Phase 1 rules (<Hard Code> prefix)
      +-- determine_nba()     -> Phase 1 rules
      +-- Return Phase 1 result (app keeps working)
```

---

## Intent Scoring Rules

| Page / Event | Intent | Points |
|-------------|--------|--------|
| Any `page_view` | GENERAL_BROWSING | +3 |
| `/troubleshooting` page_view | TROUBLESHOOTING | +15 to +20 |
| `/troubleshooting` dwell > 10s | TROUBLESHOOTING | +10 |
| `/warranty` page_view | WARRANTY_INQUIRY | +25 |
| `/warranty` form_submit | WARRANTY_INQUIRY | +30 |
| `/case-status` page_view | CASE_FOLLOW_UP | +25 |
| `/case-status` click/form | CASE_FOLLOW_UP | +30 |
| `/products` page_view | PURCHASE_SIGNAL | +5 to +15 |
| `/products` dwell > 30s | PURCHASE_SIGNAL | +15 |
| Click buy button | PURCHASE_SIGNAL | +50 |

All raw points are normalized to percentages summing to 100% via `get_normalized_intents()`.

---

## Sentiment Scoring Rules

| Event | Signal | Points |
|-------|--------|--------|
| `rage_click` (3+ clicks in 2s) | FRUSTRATED | +40 |
| Page revisit count > 2 | CONFUSED | +100 |
| Any `page_view` (cooldown) | FRUSTRATED | -30 |
| Any `page_view` (cooldown) | CONFUSED | -15 |
| Troubleshooting dwell > 10s | POSITIVE | +10 |

FRUSTRATED overrides all other sentiments when score > 20.

---

## NBA Decision Matrix

| Condition | State | Chat Trigger |
|-----------|-------|-------------|
| `sentiment == FRUSTRATED` | CRITICAL | YES |
| `segment == AT_RISK AND troubleshooting > 50%` | CRITICAL | YES |
| `troubleshooting > 60% AND NOT FRUSTRATED` | OPPORTUNITY | No |
| Default | PASSIVE | No |

Priority: CRITICAL > OPPORTUNITY > PASSIVE

---

## Segment Assignment Rules

| Priority | Segment | Condition |
|----------|---------|-----------|
| 1 | AT_RISK | Open unresolved case OR same intent in 3+ sessions in 30 days |
| 2 | VIP | Tier Gold/Platinum AND LTV > $2,000 |
| 3 | DORMANT | Last visit > 90 days ago |
| 4 | RETURNING | Has previous sessions |
| 5 | NEW_VISITOR | Default (anonymous/new) |

---

## SSE Architecture

```
Browser Tab A ──> EventSource("/api/dashboard-stream")
                       |
                       v
              stream_manager.connect(session_id)
                       |
                       v
              Creates asyncio.Queue for Tab A
              Adds to: active_connections[session_id] = [queue_A]
                       |
Browser Tab B ──> EventSource("/api/dashboard-stream")
                       |
                       v
              Creates asyncio.Queue for Tab B
              Adds to: active_connections[session_id] = [queue_A, queue_B]

When track_event fires:
  stream_manager.broadcast_to_session(session_id, message)
    |
    +-- queue_A.put(message)  --> Tab A receives update
    +-- queue_B.put(message)  --> Tab B receives update (same data)

5 SSE Event Types:
  "nba-update"            -> sse-swap into #nba-card
  "vitals-update"         -> sse-swap into #vitals
  "categorization-update" -> sse-swap into #categorization
  "timeline-update"       -> sse-swap into #timeline
  "history-update"        -> sse-swap into #history
  "chat-auto-open"        -> triggers chat.js openChat()
```

---

## Chat Tool Use (Phase 2)

```
User: "Is my warranty still valid?"
  |
  v
_llm_handle_message()
  |
  +-- Build system prompt with customer context
  +-- Call Claude API with 3 tool definitions:
  |     - get_customer_profile(customer_id)
  |     - check_warranty_status(identifier, is_serial)
  |     - get_customer_history(customer_id)
  |
  +-- Claude response: stop_reason = "tool_use"
  |     tool_use: { name: "check_warranty_status", input: { identifier: "CUST-001" } }
  |
  +-- _execute_tool("check_warranty_status", { identifier: "CUST-001" })
  |     +-- Lazy import mock_db from app.main
  |     +-- Call read_skills.check_warranty_status("CUST-001", mock_db)
  |     +-- Return JSON string of warranty records
  |
  +-- Pass tool result back to Claude (loop, max 5 iterations)
  |
  +-- Claude final response: stop_reason = "end_turn"
  |     { "reply": "Your GX-7500 warranty expired on 2025-12-15...",
  |       "escalation_required": false }
  |
  v
Return to browser: display reply in chat bubble
```

---

## Dependency Graph

```
config.py ─────────────────────────────────────────────────┐
                                                           |
models.py ──────────────────────────────────────┐          |
  (Enums + Pydantic models)                     |          |
                                                v          v
session_manager.py ────> models          routing_skills.py
                                           |    |    |
behavior_tracker.py ───> models            |    |    |
                                           |    |    |
classifier.py ─────────> models + tracker  <----+    |
                                                     |
nba_engine.py ─────────> models            <---------+
                                                     |
llm_client.py ─────────> models + config   <---------+
  |                       + classifier (fallback)
  |                       + nba_engine (fallback)
  +-- anthropic SDK       + tracker (context builder)

read_skills.py ────────> models
  ^
  |
  +-- routing_skills.py (profile + history for context)
  +-- handler.py (tool execution in Phase 2)
  +-- main.py (warranty/case page rendering)

handler.py ────────────> config + read_skills + llm_client
  |                       + anthropic SDK
  +-- _phase1_handle_message (keyword matching)
  +-- _llm_handle_message (Claude + tool use)

telegram_bridge.py ────> httpx (IPv4 forced)
  +-- send_escalation (POST to Telegram)
  +-- check_for_replies (GET from Telegram)

stream_manager.py ─────> asyncio.Queue

main.py ───────────────> ALL OF THE ABOVE
  +-- session_manager, tracker, router, stream_manager
  +-- read_skills, handle_message, telegram_bridge
  +-- Jinja2 templates, FastAPI routes, SSE endpoint
```

---

## Session Lifecycle

```
1. First HTTP request arrives
   ensure_session_id(request)
     +-- Generate UUID
     +-- Store in request.session cookie
     +-- session_manager.get_or_create(session_id) -> SessionState in RAM

2. User browses (anonymous)
   track_event() -> accumulates events, intents, sentiment in SessionState

3. User logs in
   POST /login -> validate credentials
     +-- request.session["customer_id"] = "CUST-2024-0847"
     +-- session_manager.update_customer(session_id, customer_id)
     +-- SessionState.customer_id now set
     +-- SSE broadcast: dashboard partials re-render with customer data

4. Session repair (common_context on every page load)
   If customer_id in RAM but not cookie -> copy to cookie
   If customer_id in cookie but not RAM -> copy to RAM

5. User logs out
   POST /logout
     +-- session_manager.remove_session(session_id)
     +-- request.session.clear()
     +-- HX-Redirect to /

6. Demo reset
   common_context() resets session.chat_triggered = False on every full page load
   This allows the CRITICAL->auto-open-chat demo to fire again
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Synchronous Anthropic client** | `main.py` calls `router.execute_classification()` synchronously; async would require changing the entire call chain |
| **In-memory sessions** | PoC/demo — no database needed. Sessions lost on server restart |
| **SSE over WebSocket** | Simpler, unidirectional (server→client). HTMX has native SSE support via `hx-ext="sse"` |
| **HTML-over-the-wire** | Server renders Jinja2 partials, pushes via SSE. No client-side framework needed |
| **IPv4-forced Telegram** | IPv6 connections to `api.telegram.org` fail on some corporate networks |
| **2s debounce for LLM** | Prevents API call spam during rapid navigation. Rage clicks bypass debounce |
| **Phase 1 as fallback** | Any LLM failure silently degrades to hardcoded rules. Demo never breaks |
| **Lazy import for mock_db** | `handler.py` imports `mock_db` from `app.main` inside function to avoid circular imports |
