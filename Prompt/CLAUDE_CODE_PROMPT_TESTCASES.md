# Business Test Case Generation — Claude Code Prompt
# Copy everything below this line into Claude Code in VS Code

---

Read all project files to understand the full deployed system, then generate a comprehensive business test case document.

Read these files for context:
- docs/PRD.md (Phase 1 spec — demo walkthrough, behavioral rules, enum definitions, NBA triggers)
- docs/PRD-P2.md (Phase 2 spec — AI_MODE toggle, LLM classification, fallback behavior)
- docs/LAYERS.md (Phase 1 build layers — understand what was built)
- docs/LAYERS-P2.md (Phase 2 build layers — understand what was added)
- app/engine/classifier.py (Phase 1 rule engine — the exact thresholds and scoring logic)
- app/engine/nba_engine.py (NBA trigger conditions)
- app/engine/behavior_tracker.py (intent point values, sentiment signal weights, rage click detection, cooldown logic)
- app/engine/llm_client.py (Phase 2 LLM classification and fallback)
- app/chat/handler.py (both Phase 1 keyword handler and Phase 2 LLM chat)
- app/skills/routing_skills.py (AI_MODE toggle and classification orchestration)
- app/models.py (all enums: Segment, Intent, Sentiment, NBAState — and their values)
- app/data/mock_data.json (Sarah Chen's profile, devices, warranties, cases, historical sessions)
- app/config.py (AI_MODE configuration)

Generate a file called docs/TEST_CASES.md with business-level test cases covering every user-facing scenario. This is NOT a technical test plan — it is a step-by-step manual QA script that a business stakeholder or demo operator can follow in the browser.

Format each test case as:

## TC-XXX: [Descriptive Title]
**Category:** [category]
**Precondition:** [what state the app must be in before starting]
**AI_MODE:** [phase1 | phase2 | both]

| Step | Action (what to do in the browser) | Expected Result (what you should see) |
|------|-------------------------------------|---------------------------------------|
| 1 | ... | ... |
| 2 | ... | ... |

---

Cover ALL of the following scenario categories:

### A. Dashboard Default State & Anonymous Browsing
- App loads with correct defaults (NBA=Passive, Segment=New Visitor, Sentiment=Neutral)
- Propensity gauge shows GENERAL_BROWSING at 100% initially
- All 5 dashboard sections render correctly
- Journey timeline is empty with placeholder text

### B. Intent Accumulation & Propensity Gauge Changes
- Browsing Home → product categories → PURCHASE_SIGNAL rises
- Navigating to Troubleshooting → sub-category → KB article → TROUBLESHOOTING intent climbs step by step
- Visiting Warranty Check page → WARRANTY_INQUIRY rises
- Visiting Case Status page → CASE_FOLLOW_UP rises
- Each navigation adds GENERAL_BROWSING baseline (+3 pts) — verify it never dominates when specific intent actions occur
- Propensity gauge bars reorder as dominant intent changes

### C. Sentiment Lifecycle (Full Progression)
- Start: NEUTRAL (default, no signals)
- Steady browsing with 10-60s dwell on pages → shifts to POSITIVE
- Revisit same page 2+ times → shifts to CONFUSED
- Include the exact page revisit count that triggers CONFUSED (visit count > 2 per behavior_tracker.py)
- Rapid page switching or rage clicks → shifts to FRUSTRATED
- After FRUSTRATED: one normal page click triggers cooldown → sentiment should recover (the -30 cooldown in behavior_tracker.py)
- Verify sentiment insight text changes with each state (Phase 1: hardcoded text, Phase 2: AI-generated)

### D. Sentiment Signal: Rage Click Detection
- Specific test: click same area 3+ times within 2 seconds
- Dashboard should show FRUSTRATED sentiment
- Sentiment insight should reference difficulty/frustration
- One normal navigation after rage click → verify cooldown kicks in

### E. NBA State Transitions (Passive → Opportunity → Critical)
- PASSIVE: default state, verify green indicator and "Monitor Behavior" text
- OPPORTUNITY trigger: TROUBLESHOOTING intent > 60% AND sentiment ≠ FRUSTRATED → yellow indicator, "Suggest Self-Service Resources"
- CRITICAL trigger path 1: sentiment = FRUSTRATED → red indicator, "Proactive Outreach Recommended"
- CRITICAL trigger path 2: segment = AT_RISK AND TROUBLESHOOTING intent > 50% → also CRITICAL
- Verify priority: CRITICAL overrides OPPORTUNITY

### F. Chat Widget Behavior
- Manual open: click "Need Help?" button → chat opens
- Manual close: close button works
- Chat auto-open: when NBA goes CRITICAL with should_trigger_chat=true → chat opens automatically with proactive system message
- Auto-open should only fire ONCE per session (the chat_triggered flag)
- Verify chat header shows "🤖 AI Assistant" in AI mode

### G. Chat Responses (Phase 1 vs Phase 2)
- Phase 1 (AI_MODE=phase1):
  - Type "warranty" or "expired" → hardcoded warranty response with <Hard Code> prefix
  - Type "flickering" or "monitor" → hardcoded display issue response with <Hard Code> prefix
  - Type "buy" or "price" → hardcoded pricing response
  - Type anything else → default fallback response
  - Type "agent" or "transfer" → escalation trigger
- Phase 2 (AI_MODE=phase2):
  - Same inputs → contextual AI responses WITHOUT <Hard Code> prefix
  - AI should reference actual customer data (e.g., "your GX-7500", "warranty expired")
  - Indirect escalation: "I give up" or "this isn't working" → should also trigger escalation
  - Verify AI responses are different each time (not hardcoded)

### H. Login & Profile Merge
- Login with sarah.chen@email.com / demo123
- Dashboard transforms: Customer Vitals populate (name, tier, LTV, open cases)
- Segment changes from NEW_VISITOR to AT_RISK (Sarah has open case + recurrent issue)
- Historical Sessions table appears showing 2 past visits
- ⚠️ RECURRENT ISSUE badge appears (same TROUBLESHOOTING intent across 3+ sessions)
- Login with wrong credentials → error message, no state change

### I. Logged-In Page Auto-Population
- After login, navigate to Warranty Check:
  - Both devices auto-display: GX-7500 (❌ Expired, red badge) and TX-1000 (✅ Active, green badge)
  - Extended warranty upsell banner visible for expired device
  - Search form still available below
- After login, navigate to Case Status:
  - Both cases auto-display: CASE-2025-0312 (✅ Resolved) and CASE-2026-0891 (🔴 Open)
  - Click open case → expands with details, interaction log
  - Linked case reference visible (CASE-2026-0891 links to CASE-2025-0312)

### J. Journey Timeline
- Each page navigation adds a node to the horizontal timeline
- Node shows: category label on top, detail + dwell below
- Node color: green for positive/neutral, red for frustrated/confused, amber for cautious
- Timeline scrolls horizontally when nodes exceed visible area
- Verify nodes appear in chronological order (left to right)

### K. Telegram Escalation (End-to-End)
- Open chat → click "Transfer to Live Agent"
- Telegram notification fires with: customer name, tier, sentiment, event count
- Reply from Telegram → message appears in web chat
- Chat header changes from "🤖 AI Assistant" to "👤 Live Agent"

### L. AI_MODE Toggle (Phase Switch)
- Start with AI_MODE=phase2, browse around → verify AI-generated insights (no <Hard Code>)
- Stop server, change .env to AI_MODE=phase1, restart
- Same browsing → verify <Hard Code> prefixed insights return
- Verify no errors in console during switch

### M. Phase 2 Fallback Resilience
- Set AI_MODE=phase2 but ANTHROPIC_API_KEY to invalid value
- Browse the app → dashboard should still update with <Hard Code> fallback
- Console should show fallback warning messages
- Chat should fall back to keyword matching

### N. Full Demo Walkthrough (The 8-Minute Script)
- This is the complete end-to-end scenario from PRD Section 8
- Cover all 6 scenes in sequence as one continuous test
- Document expected state at each transition point
- Run once with AI_MODE=phase1, once with AI_MODE=phase2

### O. Edge Cases
- Logout → verify session clears, dashboard resets to anonymous defaults
- Rapid navigation (5+ pages in 3 seconds) → should trigger FRUSTRATED sentiment
- Open chat, type nothing, close → no errors
- Double-click login button → no duplicate session issues
- Refresh page mid-session → session state should persist (cookie-based)

Make sure every test case references the EXACT expected enum values, badge colors, text prefixes, and UI indicators. The person running these tests should be able to verify pass/fail without reading any code.
