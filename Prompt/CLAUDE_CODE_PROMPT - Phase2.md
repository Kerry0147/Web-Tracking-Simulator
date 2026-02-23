# Phase 2 Implementation — Claude Code Prompt
# Copy everything below this line into Claude Code in VS Code

---

Read docs/PRD-P2.md and docs/LAYERS-P2.md completely before writing any code.

Then read these existing Phase 1 files to understand the current codebase:
- app/models.py (all enums and Pydantic models — this is the shared contract)
- app/engine/classifier.py (Phase 1 rule engine — becomes fallback)
- app/engine/nba_engine.py (Phase 1 NBA logic — becomes fallback)
- app/engine/behavior_tracker.py (understand SessionState structure)
- app/skills/routing_skills.py (current orchestration — you will modify this)
- app/skills/read_skills.py (mock data retrieval — these become chat tools)
- app/chat/handler.py (current keyword handler — you will modify this)
- app/main.py (understand how routing_skills and handler are called — do NOT modify this file)
- .env (current environment variables)
- requirements.txt (current dependencies)

Implement Phase 2 in layer order as described in LAYERS-P2.md:

## P2-Layer 1: Config & LLM Client Foundation

Create app/config.py:
- Load .env via python-dotenv
- Export: AI_MODE (str, default "phase1"), ANTHROPIC_API_KEY (str), LLM_MODEL (str, "claude-haiku-4-5-20251001"), LLM_TIMEOUT (int, 10), LLM_MAX_TOKENS (int, 1024)

Create app/engine/llm_client.py:
- Use the synchronous anthropic.Anthropic client (NOT async) — this is critical because main.py calls routing_skills synchronously
- build_session_context(session, customer_data) → readable text summary for LLM
- llm_classify_behavior(session, customer_data) → calls Claude API, parses JSON, validates enums, returns tuple[ClassificationResult, NBAResult]
- safe_llm_classify(session, customer_data) → wraps llm_classify_behavior in try/except, falls back to Phase 1 classifier.py + nba_engine.py on any failure, prints warning
- should_call_llm(session_id) → debounce check, returns True if >2 seconds since last call or rage_click detected
- Follow the system prompt and JSON schema exactly as specified in PRD-P2.md Section 4.3-4.4

Update requirements.txt: add anthropic
Update .env: add AI_MODE=phase1 (keep existing variables unchanged)

After creating these files, pause and verify:
1. app/config.py loads correctly
2. build_session_context produces readable output
3. safe_llm_classify falls back gracefully when API key is invalid

## P2-Layer 2: Classification Swap & Chat AI

Modify app/skills/routing_skills.py:
- Import AI_MODE from app.config
- Import safe_llm_classify and should_call_llm from app.engine.llm_client
- Keep ALL existing Phase 1 imports
- In execute_classification(): add AI_MODE check
  - If phase2 and should_call_llm: call safe_llm_classify (which has built-in fallback)
  - If phase1 or debounce says skip: use original classify_behavior + determine_nba
- Add module-level cache _last_result dict so debounced calls return cached results
- KEEP the method synchronous (safe_llm_classify uses sync Anthropic client)
- Do NOT change the return type: tuple[ClassificationResult, NBAResult]

Modify app/chat/handler.py:
- Rename existing handle_message to _phase1_handle_message (keep it entirely intact)
- Create new handle_message that checks AI_MODE:
  - phase1 → call _phase1_handle_message
  - phase2 → call _llm_handle_message with try/except fallback to _phase1_handle_message
- Create _llm_handle_message:
  - Use synchronous Anthropic client with tool use
  - System prompt per PRD-P2.md Section 5.3
  - Include customer context (profile, devices, warranty, cases, sentiment) in system prompt
  - Define 3 tools: get_customer_profile, check_warranty_status, get_customer_history
  - Handle tool_use responses by calling the matching read_skills function
  - For mock_data access: use lazy import of mock_db from app.main inside the function to avoid circular imports
  - Parse response as JSON {reply, escalation_required}
  - Return the dict in same format as Phase 1

CRITICAL RULES:
- Do NOT modify app/main.py
- Do NOT modify app/engine/classifier.py (preserve as fallback)
- Do NOT modify app/engine/nba_engine.py (preserve as fallback)
- Do NOT modify any templates or static files
- Do NOT delete any existing functions — only add new ones and rename
- The default AI_MODE in .env must be "phase1" so the app works without a Claude API key
