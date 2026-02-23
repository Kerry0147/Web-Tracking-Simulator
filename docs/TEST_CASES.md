# Project ECHO — Business Test Cases
## Manual QA Script for Demo Operators & Business Stakeholders

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Date | February 12, 2026 |
| Covers | Phase 1 (Hardcoded) + Phase 2 (AI-Powered) |
| Prerequisites | Server running via `uvicorn app.main:app --reload --port 8000` |
| Browser | Chrome or Edge, 1280px+ width, DevTools console open (F12) |
| Demo Credentials | `sarah.chen@email.com` / `demo123` |

---

## How to Use This Document

1. Each test case is self-contained with preconditions, steps, and expected results
2. **AI_MODE** indicates which `.env` setting the test requires:
   - `phase1` = hardcoded rules (default, no API key needed)
   - `phase2` = Claude AI (requires valid `ANTHROPIC_API_KEY`)
   - `both` = run the test twice, once per mode
3. After changing `.env`, **restart the server** for changes to take effect
4. Look for the **exact** text, colors, and indicators described — no interpretation needed

---

## A. Dashboard Default State & Anonymous Browsing

---

## TC-001: App Loads with Correct Default State
**Category:** A. Dashboard Defaults
**Precondition:** Fresh server start. Not logged in. No prior browsing.
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open `http://localhost:8000` in browser | Split-screen loads: left pane (~60% width, light background) shows ProBook home page; right pane (~40% width, dark navy background) shows the dashboard |
| 2 | Look at the top of the right pane | "LIVE ANALYSIS" header with a green pulsing dot and "ONLINE" label in green text |
| 3 | Look at the NBA card (topmost section) | Green border. Icon: 👁️. State label shows "PASSIVE" in green text. Action text present (Phase 1: starts with `<Hard Code>`, Phase 2: natural language) |
| 4 | Look at Customer Vitals section | Shows "Anonymous Visitor" with a gray circle containing "?" — no profile fields displayed |
| 5 | Look at the Propensity Gauge | GENERAL_BROWSING at 100% (gray bar) — no other intents have scores yet |
| 6 | Look at Live Categorization — Segment card | Badge shows "NEW_VISITOR" with blue background (`bg-blue-900` / `text-blue-200`) |
| 7 | Look at Live Categorization — Intent card | Shows "GENERAL_BROWSING" as the primary intent |
| 8 | Look at Live Categorization — Sentiment card | Emoji: 😐. Label: "NEUTRAL" |
| 9 | Look at Journey Timeline section | Empty track with placeholder text or minimal nodes |
| 10 | Look at Historical Sessions section | Shows "Login to view session history" or similar message — table not visible |

---

## TC-002: All Five Dashboard Sections Render
**Category:** A. Dashboard Defaults
**Precondition:** Fresh app load, not logged in
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open the app and examine the right pane top-to-bottom | Five distinct sections visible, stacked vertically in a scrollable sidebar |
| 2 | Identify Section A | 🎯 Next Best Action card — colored border, icon, state label, action text |
| 3 | Identify Section B | 👤 Customer Vitals + 📊 Propensity Gauge — profile area + horizontal bar chart |
| 4 | Identify Section C | 🧠 Live Categorization — three sub-cards: Segment (🏷️), Intent (🎯), Sentiment (emoji) |
| 5 | Identify Section D | 🗺️ Journey Timeline — horizontal track area |
| 6 | Identify Section E | 📅 Historical Sessions — placeholder when not logged in |

---

## B. Intent Accumulation & Propensity Gauge Changes

---

## TC-003: Purchase Signal Intent Rises on Product Browsing
**Category:** B. Intent Accumulation
**Precondition:** Fresh session, not logged in
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open the app — note the Propensity Gauge | GENERAL_BROWSING at 100% |
| 2 | Click "Home" in the nav bar | Propensity Gauge still shows GENERAL_BROWSING dominant (baseline +3 pts per page view) |
| 3 | Click on "Gaming Laptops" product category card | PURCHASE_SIGNAL appears in the gauge. Gauge now shows two bars: GENERAL_BROWSING and PURCHASE_SIGNAL. PURCHASE_SIGNAL should have +5 pts for browsing category |
| 4 | Click on a specific product (e.g., GX-7500 detail) | PURCHASE_SIGNAL bar grows further (+15 pts for product detail view). It may now exceed GENERAL_BROWSING |
| 5 | Click on another product category (e.g., "Workstations") | PURCHASE_SIGNAL continues to accumulate. The gauge bars reorder so the highest intent is on top |

---

## TC-004: Troubleshooting Intent Climbs Step by Step
**Category:** B. Intent Accumulation
**Precondition:** Fresh session, not logged in
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open the app — gauge shows GENERAL_BROWSING at 100% | Starting state confirmed |
| 2 | Click "Troubleshooting" in the nav bar | TROUBLESHOOTING appears in the gauge (+15 pts). GENERAL_BROWSING also gets +3 pts baseline. Gauge shows both bars |
| 3 | Click on "Monitor" sub-category | TROUBLESHOOTING grows further (+15–20 pts for deeper troubleshooting page). It should now be the dominant intent |
| 4 | Click on "Screen Flickering Fix" KB article (KB-MON-001) | TROUBLESHOOTING jumps significantly (+20 pts for opening a KB article). Should now be at 70%+ |
| 5 | Wait 15 seconds on the article page, then navigate away | On navigation, dwell time >10s adds +10 more pts to TROUBLESHOOTING. Verify intent bar is the longest |
| 6 | Check the Intent card in Live Categorization | Primary Intent should show "TROUBLESHOOTING" |

---

## TC-005: Warranty Inquiry Intent Rises
**Category:** B. Intent Accumulation
**Precondition:** Fresh session, not logged in
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open the app, then click "Warranty Check" in the nav bar | WARRANTY_INQUIRY appears in the propensity gauge (+25 pts for visiting Warranty page) |
| 2 | Check the gauge ordering | WARRANTY_INQUIRY should be the dominant intent (higher than GENERAL_BROWSING baseline) |

---

## TC-006: Case Follow-Up Intent Rises
**Category:** B. Intent Accumulation
**Precondition:** Fresh session, not logged in
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open the app, then click "Case Status" in the nav bar | CASE_FOLLOW_UP appears in the propensity gauge (+25 pts) |
| 2 | Check the gauge ordering | CASE_FOLLOW_UP should be the dominant intent |

---

## TC-007: General Browsing Baseline Never Dominates Specific Intents
**Category:** B. Intent Accumulation
**Precondition:** Fresh session, not logged in
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate: Home → Troubleshooting → Monitor → Screen Flickering Fix | After 4 page views, GENERAL_BROWSING has ~12 pts (4 × 3 pts). TROUBLESHOOTING has ~50+ pts. Verify TROUBLESHOOTING is clearly dominant in the gauge |
| 2 | Navigate to 3 more random pages (e.g., Home, Warranty, Case Status) | GENERAL_BROWSING gains +9 more pts. But specific intents from earlier still dominate. TROUBLESHOOTING should remain the #1 bar |

---

## C. Sentiment Lifecycle (Full Progression)

---

## TC-008: Default Sentiment is NEUTRAL
**Category:** C. Sentiment Lifecycle
**Precondition:** Fresh session, not logged in
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open the app | Sentiment card shows: Emoji 😐, Label "NEUTRAL" |
| 2 | Click one or two pages casually | Sentiment stays NEUTRAL (no strong signals yet) |

---

## TC-009: Steady Dwell Triggers POSITIVE Sentiment
**Category:** C. Sentiment Lifecycle
**Precondition:** Fresh session, not logged in
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to Troubleshooting → Monitor → any KB article | Arrive on KB article page |
| 2 | Stay on the page for 15–30 seconds reading the content, then click to another page | The `page_leave` event fires with dwell_time > 10s. This adds +10 to POSITIVE sentiment signal in behavior_tracker. Sentiment card may shift to 😊 POSITIVE (shown in green text) |
| 3 | Read the Sentiment Insight text below the label | Phase 1: `<Hard Code> Steady dwell times and linear navigation indicate good engagement.` Phase 2: AI-generated text about engagement |

---

## TC-010: Page Revisits Trigger CONFUSED Sentiment
**Category:** C. Sentiment Lifecycle
**Precondition:** Some browsing done (2+ pages visited), not logged in
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to Troubleshooting → Monitor → Screen Flickering Fix (KB-MON-001) | First visit to this article — visit count = 1 |
| 2 | Navigate away (e.g., back to Monitor list) | Visit count for that article = 1, no CONFUSED trigger yet |
| 3 | Navigate back to the SAME Screen Flickering Fix article | Visit count = 2, still no CONFUSED trigger (threshold is >2) |
| 4 | Navigate away and then back to the SAME article a THIRD time | Visit count = 3 (>2). This triggers +100 CONFUSED signal. Sentiment card should show: Emoji 😕, Label "CONFUSED" |
| 5 | Check console output (F12) | Should see: `⚠️ Revisit #3 on /troubleshooting/monitor/KB-MON-001 (+100 Confused)` |
| 6 | Read the Sentiment Insight text | Phase 1: `<Hard Code> Navigation loops detected. Customer is revisiting the same pages multiple times.` Phase 2: AI-generated text about confusion |

---

## TC-011: Rage Clicks Trigger FRUSTRATED and Cooldown Recovery
**Category:** C. Sentiment Lifecycle
**Precondition:** Fresh session, not logged in
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to any page in the app | Sentiment is NEUTRAL or any non-FRUSTRATED state |
| 2 | Rapidly click the same area 3+ times within 2 seconds (rage click) | `rage_click` event fires. +40 to FRUSTRATED signal. If FRUSTRATED score exceeds 20, Sentiment shifts to 😤 FRUSTRATED (red text). Console shows: `🤬 RAGE CLICK DETECTED!` |
| 3 | Read the Sentiment Insight text | Phase 1: `<Hard Code> Behavioral signals indicate difficulty — rapid page switching and repeated page revisits suggest the customer is not finding what they need.` Phase 2: AI-generated |
| 4 | Click normally on a navigation link (one page view) | Cooldown fires: FRUSTRATED score reduced by 30 pts. Console shows: `❄️ Sentiment Cooling Down... (Frustrated Score: X)` |
| 5 | Check Sentiment card after normal click | If FRUSTRATED score dropped below 20, sentiment should recover to a non-FRUSTRATED state (NEUTRAL, POSITIVE, or whatever the next highest signal is) |

---

## D. Sentiment Signal: Rage Click Detection

---

## TC-012: Rage Click Detection Mechanics
**Category:** D. Rage Click
**Precondition:** Fresh session, any page loaded
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open any page and position your cursor over a clickable element | Ready to test |
| 2 | Click the same element rapidly — exactly 3 times within 2 seconds | After the 3rd click, behavior.js detects rage click (threshold: 3 clicks in 2000ms). Event sent to server |
| 3 | Check the dashboard Sentiment card | Should show 😤 FRUSTRATED in red text (`text-red-400`) |
| 4 | Check the NBA card | If this is the only FRUSTRATED signal and score > 20, NBA should transition to 🚨 CRITICAL with red border, `animate-pulse` animation, and text "Proactive Outreach Recommended" (or AI equivalent) |
| 5 | Click normally on one navigation link | FRUSTRATED score drops by 30 (cooldown). Check console: `❄️ Sentiment Cooling Down...` If score falls below 20, sentiment should recover |

---

## E. NBA State Transitions

---

## TC-013: NBA Starts as PASSIVE
**Category:** E. NBA Transitions
**Precondition:** Fresh session, not logged in
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open the app | NBA card shows: green border (`border-green-500/50`), icon 👁️, state "PASSIVE" in green text. Action text present |
| 2 | Browse a few pages casually | NBA stays PASSIVE — no trigger conditions met |

---

## TC-014: NBA Transitions to OPPORTUNITY
**Category:** E. NBA Transitions
**Precondition:** Fresh session, not logged in, no rage clicks
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate: Troubleshooting → Monitor → Screen Flickering Fix article | TROUBLESHOOTING intent should climb |
| 2 | Stay on the article for 15+ seconds, then navigate away | TROUBLESHOOTING gets extra dwell points. Intent should be well above 60% |
| 3 | Navigate to Troubleshooting → Monitor → External Monitor Not Detected | More TROUBLESHOOTING points accumulate. Intent should be at 70%+ |
| 4 | Check the NBA card | Should show: yellow border (`border-yellow-500/50`), icon 💡, state "OPPORTUNITY" in yellow text. Action text (Phase 1): `<Hard Code> Suggest Self-Service Resources. Offer specific KB articles for monitor flickering.` |
| 5 | Verify sentiment is NOT FRUSTRATED | This is required for OPPORTUNITY — if sentiment is FRUSTRATED, NBA would be CRITICAL instead |

---

## TC-015: NBA Transitions to CRITICAL via FRUSTRATED Sentiment
**Category:** E. NBA Transitions
**Precondition:** Any session state
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to any page | Starting state noted |
| 2 | Perform a rage click (3+ rapid clicks on same area within 2 seconds) | FRUSTRATED sentiment triggers |
| 3 | Check the NBA card | Should show: red border (`border-red-500/50`), red background glow (`bg-red-900/20`), `animate-pulse` animation, icon 🚨, state "CRITICAL" in red text. Action text (Phase 1): `<Hard Code> Proactive Outreach Recommended. Customer is struggling with a recurring technical issue.` |
| 4 | Verify `should_trigger_chat` is true | Chat widget should auto-open within ~1 second (see TC-019) |

---

## TC-016: NBA Transitions to CRITICAL via AT_RISK + Troubleshooting
**Category:** E. NBA Transitions
**Precondition:** Not logged in yet, some troubleshooting browsing done
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate: Troubleshooting → Monitor → Screen Flickering Fix → dwell 15s → navigate away | Build up TROUBLESHOOTING intent to >50% |
| 2 | Login as Sarah Chen (sarah.chen@email.com / demo123) | Segment changes to AT_RISK (Sarah has open case + 3 recurrent TROUBLESHOOTING sessions). Verify Segment badge shows "AT_RISK" with orange background |
| 3 | Check the NBA card | With AT_RISK segment AND TROUBLESHOOTING intent > 50%, NBA should be 🚨 CRITICAL (even without FRUSTRATED sentiment). Red border, pulse animation, icon 🚨 |

---

## TC-017: CRITICAL Overrides OPPORTUNITY Priority
**Category:** E. NBA Transitions
**Precondition:** Session with high TROUBLESHOOTING intent (>60%)
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Build TROUBLESHOOTING to >60% without frustration | NBA should be at OPPORTUNITY (yellow) |
| 2 | Now perform a rage click (3+ rapid clicks) | FRUSTRATED triggers. NBA should immediately jump to CRITICAL (red) — not stay at OPPORTUNITY |
| 3 | Verify NBA card | Red border, 🚨 icon, "CRITICAL" label. CRITICAL takes priority over OPPORTUNITY |

---

## F. Chat Widget Behavior

---

## TC-018: Manual Chat Open and Close
**Category:** F. Chat Widget
**Precondition:** App loaded, any state
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Look at the bottom-right area of the left pane | Blue floating button visible: "💬 Need Help?" pill |
| 2 | Click the "💬 Need Help?" button | Chat window opens as an overlay. Header shows "AI Assistant" with green dot indicator and "Automated Support" subtitle |
| 3 | Verify the chat window elements | Message area (empty or with welcome), text input field with "Type a message..." placeholder, send button, "Talk to a human? Connect Now" escalation banner in header area |
| 4 | Click the close button (X) on the chat window | Chat window closes/hides. The "💬 Need Help?" button reappears |
| 5 | Click the button again | Chat window reopens in the same state |

---

## TC-019: Chat Auto-Opens on CRITICAL NBA
**Category:** F. Chat Widget
**Precondition:** Chat is closed, NBA is not yet CRITICAL
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Ensure the chat window is closed | "💬 Need Help?" button visible |
| 2 | Trigger CRITICAL NBA (e.g., rage click 3+ times rapidly) | NBA card turns red with 🚨 CRITICAL |
| 3 | Wait ~1 second | Chat window auto-opens without user clicking the button |
| 4 | Check the chat messages area | A system message appears: "I noticed you seem to be having a recurring issue. Can I assist you directly?" (or similar proactive message) |
| 5 | Close the chat window, then trigger CRITICAL again (navigate normally to reset, then rage click again) | Chat should NOT auto-open a second time in the same session (the `chat_triggered` / `window.hasAutoOpened` flag prevents it) |

---

## TC-020: Chat Auto-Open Fires Only Once Per Session
**Category:** F. Chat Widget
**Precondition:** CRITICAL NBA already triggered once and chat auto-opened
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Close the auto-opened chat | Chat closes |
| 2 | Navigate normally for a bit to let sentiment cool down | NBA may drop back to OPPORTUNITY or PASSIVE |
| 3 | Rage click again to trigger CRITICAL NBA once more | NBA goes CRITICAL again (red card) |
| 4 | Wait 2 seconds | Chat does NOT auto-open this time — the one-shot flag prevents duplicate auto-opens |
| 5 | Manually click "💬 Need Help?" | Chat can still be opened manually — the flag only blocks auto-open |

---

## G. Chat Responses (Phase 1 vs Phase 2)

---

## TC-021: Phase 1 Chat — Warranty Keyword Response
**Category:** G. Chat Responses
**Precondition:** App running, chat open
**AI_MODE:** phase1

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open the chat widget | Chat window visible with input field |
| 2 | Type "Is my warranty still valid?" and press Enter/Send | Bot response appears: `<Hard Code> I can see you're asking about warranty coverage. Let me look into your account details. It looks like your GX-7500 warranty expired on 2026-01-15.` |
| 3 | Verify the response has the `<Hard Code>` prefix | The literal text `<Hard Code>` must appear at the start of the reply |

---

## TC-022: Phase 1 Chat — Monitor/Flickering Keyword Response
**Category:** G. Chat Responses
**Precondition:** Chat open
**AI_MODE:** phase1

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Type "My monitor keeps flickering" and send | Bot response: `<Hard Code> I understand you're experiencing display issues. Based on your activity, I see you've been looking at article KB-MON-002. Did those steps help?` |
| 2 | Verify `<Hard Code>` prefix present | Confirmed |

---

## TC-023: Phase 1 Chat — Purchase Keyword Response
**Category:** G. Chat Responses
**Precondition:** Chat open
**AI_MODE:** phase1

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Type "How much does the GX-7500 cost?" and send | Bot response: `<Hard Code> I can help with product pricing. The ProBook GX-7500 is currently listed at $2,499. Would you like to check stock?` |

---

## TC-024: Phase 1 Chat — Default Fallback Response
**Category:** G. Chat Responses
**Precondition:** Chat open
**AI_MODE:** phase1

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Type "Hello, I need some help" and send | Bot response: `<Hard Code> Thank you for reaching out. I am the ProBook AI. How can I assist you today?` (no keyword matched, so default fires) |

---

## TC-025: Phase 1 Chat — Escalation Keyword Detection
**Category:** G. Chat Responses
**Precondition:** Chat open
**AI_MODE:** phase1

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Type "Can I talk to a human agent?" and send | Bot response: `<Hard Code> I can certainly transfer you to a human agent.` |
| 2 | Verify escalation triggered | The escalation flow should activate (Telegram notification attempted, chat header may change) |

---

## TC-026: Phase 2 Chat — Contextual AI Responses
**Category:** G. Chat Responses
**Precondition:** AI_MODE=phase2 with valid ANTHROPIC_API_KEY, logged in as Sarah Chen
**AI_MODE:** phase2

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Login as Sarah Chen, open the chat | Chat window open, AI has customer context |
| 2 | Type "My monitor keeps flickering" and send | AI response is contextual and specific — may reference "your GX-7500", the open case, or warranty expiration. Response does NOT start with `<Hard Code>` |
| 3 | Type "Is my warranty still valid?" and send | AI may use tools to look up warranty data. Response should reference the actual warranty end date (2025-12-15, expired) for the GX-7500 and active status for the TX-1000 |
| 4 | Send the same question again | Response should be different from the first time (not hardcoded — AI generates fresh text each time) |

---

## TC-027: Phase 2 Chat — Indirect Escalation Detection
**Category:** G. Chat Responses
**Precondition:** AI_MODE=phase2, chat open
**AI_MODE:** phase2

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Type "I give up, this isn't working" and send | AI should recognize the escalation intent even though no keyword like "agent" or "transfer" appears. Response should offer to connect to a human. `escalation_required` should be true, triggering the escalation flow |
| 2 | Start a fresh chat. Type "I've been trying everything and nothing helps, I need someone to fix this" | AI should also detect this as an escalation request and trigger the escalation flow |

---

## TC-028: Phase 2 Chat — No Hard Code Prefix
**Category:** G. Chat Responses
**Precondition:** AI_MODE=phase2
**AI_MODE:** phase2

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Send any message in the chat | Response text must NOT contain the literal string `<Hard Code>` anywhere |
| 2 | Send 3 different messages | All responses should be natural language without any `<Hard Code>` prefix |

---

## H. Login & Profile Merge

---

## TC-029: Login with Valid Credentials
**Category:** H. Login
**Precondition:** Not logged in, some anonymous browsing done
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click "Sign In" button (top-right of nav bar) | Login modal or form appears with email and password fields |
| 2 | Enter `sarah.chen@email.com` and `demo123`, click login | Login succeeds. Page reloads/updates |
| 3 | Check the nav bar | Should now show "Sarah Chen" (or similar logged-in indicator) instead of "Sign In" |
| 4 | Check Customer Vitals on the dashboard | Profile fields populated: 👤 Sarah Chen, ⭐ Gold tier (yellow text), 💰 $3,249.97 LTV (green text). Avatar area shows initials instead of "?" |
| 5 | Check Segment card | Should show "AT_RISK" with orange background badge (`bg-orange-900` / `text-orange-200` / `border-orange-700`). Sarah qualifies because she has an open case (CASE-2026-0891) AND recurrent TROUBLESHOOTING intent across 3+ sessions |
| 6 | Check Historical Sessions section | Table now visible with 2 past sessions: SESS-2025-0815 (Aug 15, 2025, TROUBLESHOOTING intent, CAUTIOUS sentiment) and SESS-2026-0122 (Jan 22, 2026, TROUBLESHOOTING intent, FRUSTRATED sentiment) |
| 7 | Look for the Recurrence Badge | "⚠️ RECURRENT ISSUE" badge should appear above or near the history table — red pulsing badge (`bg-red-900/50 text-red-300 animate-pulse border-red-800`). This fires because TROUBLESHOOTING appears in 3+ sessions (2 historical + current) |

---

## TC-030: Login with Invalid Credentials
**Category:** H. Login
**Precondition:** Not logged in
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click "Sign In" and enter `wrong@email.com` / `badpass` | Error message appears (red text): "Invalid credentials" |
| 2 | Check the dashboard | No change — Customer Vitals still show "Anonymous Visitor", Segment still "NEW_VISITOR" |
| 3 | Check the nav bar | Still shows "Sign In" — login did not succeed |

---

## I. Logged-In Page Auto-Population

---

## TC-031: Warranty Check Page — Logged In Auto-Display
**Category:** I. Logged-In Pages
**Precondition:** Logged in as Sarah Chen
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click "Warranty Check" in the nav bar | Page loads with auto-populated device cards — no need to enter serial numbers |
| 2 | Find the GX-7500 device card | Shows: "ProBook GX-7500 Pro Gaming Laptop", Serial: GX7500-2024-A1847, Purchase: 2024-12-15. Warranty badge: ❌ Expired (red badge). Warranty type: Standard 1-Year, End date: 2025-12-15 |
| 3 | Find the TX-1000 device card | Shows: "ProBook TX-1000 Tablet", Serial: TX1000-2025-B2201, Purchase: 2025-06-20. Warranty badge: ✅ Active (green badge). Warranty type: Standard 1-Year, End date: 2026-06-20 |
| 4 | Look for extended warranty upsell | The expired GX-7500 should show an "Extended Warranty Available" banner or similar upsell indicator |
| 5 | Scroll down below the auto-displayed devices | A serial number search form should still be available for additional lookups |

---

## TC-032: Case Status Page — Logged In Auto-Display
**Category:** I. Logged-In Pages
**Precondition:** Logged in as Sarah Chen
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click "Case Status" in the nav bar | Page loads with auto-populated case cards |
| 2 | Find the CASE-2025-0312 card | Shows: Case ID "CASE-2025-0312", Subject "Monitor flickering during gaming", Device "ProBook GX-7500 Pro Gaming Laptop", Status badge: ✅ Resolved (green badge), Created: 2025-08-15 |
| 3 | Find the CASE-2026-0891 card | Shows: Case ID "CASE-2026-0891", Subject "Monitor flickering returned — same issue", Status badge: 🔴 Open (red badge), Created: 2026-01-22 |
| 4 | Click on the open case (CASE-2026-0891) to expand | Expanded view shows: interaction log with 2 entries (Chat on 2026-01-22, Email on 2026-01-24), and a linked case reference to CASE-2025-0312 |
| 5 | Verify linked case reference | "Linked Case: CASE-2025-0312" should be visible and potentially clickable to view the resolved case |
| 6 | Scroll down | A case number search form should still be available below the auto-displayed cases |

---

## J. Journey Timeline

---

## TC-033: Timeline Nodes Appear on Navigation
**Category:** J. Journey Timeline
**Precondition:** Fresh session
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open the app — check the Journey Timeline section | Empty or minimal — placeholder text like "Waiting for activity..." |
| 2 | Click "Troubleshooting" in the nav bar | A new node appears in the timeline. Node shows category label and page detail |
| 3 | Click "Monitor" sub-category | A second node appears to the right of the first, connected by a line |
| 4 | Click "Screen Flickering Fix" article | A third node appears. Timeline now shows 3 connected dots left-to-right |
| 5 | Navigate to "Warranty Check" | A fourth node appears. Nodes are in chronological order: Troubleshooting → Monitor → KB article → Warranty |

---

## TC-034: Timeline Node Colors by Page Category
**Category:** J. Journey Timeline
**Precondition:** Active session with navigation history
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to a Troubleshooting page | The corresponding timeline node has a blue color (`bg-blue-500`) |
| 2 | Navigate to the Warranty Check page | The corresponding timeline node has a purple color (`bg-purple-500`) |
| 3 | Navigate to the Case Status page | The corresponding timeline node has an orange color (`bg-orange-500`) |
| 4 | Navigate to the Home page or products | The corresponding timeline node has a gray color (`bg-gray-400`) |

---

## TC-035: Timeline Horizontal Scroll
**Category:** J. Journey Timeline
**Precondition:** Active session
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate through 8+ different pages | 8+ nodes appear in the timeline |
| 2 | Check if timeline overflows the visible area | Timeline container should scroll horizontally. Use mouse wheel or drag to scroll |
| 3 | Scroll to the rightmost node | The most recent page visited is the rightmost (last) node |

---

## K. Telegram Escalation (End-to-End)

---

## TC-036: Telegram Escalation via Chat
**Category:** K. Telegram Escalation
**Precondition:** Logged in as Sarah Chen. Valid TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env. Telegram app open on operator's phone
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open the chat widget | Chat window visible |
| 2 | Click "Connect Now" (or "Transfer to Live Agent" button in the escalation banner) | Escalation initiated |
| 3 | Check chat header | Title changes from "AI Assistant" to "Live Support". Subtitle briefly shows "Connecting to Agent..." then changes to "Agent Notified". Status dot may change from green to yellow briefly, then back to green |
| 4 | Check operator's Telegram | A notification should arrive with context: customer name (Sarah Chen), tier (Gold), sentiment, visit count, and issue summary |
| 5 | Reply from Telegram (type a response as the operator) | The reply should appear in the web chat as a message from the live agent (displayed with 👨‍💼 avatar instead of 🤖) |

---

## L. AI_MODE Toggle (Phase Switch)

---

## TC-037: Switch from Phase 2 to Phase 1
**Category:** L. AI_MODE Toggle
**Precondition:** .env has AI_MODE=phase2 with valid ANTHROPIC_API_KEY
**AI_MODE:** phase2 → phase1

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Start server with AI_MODE=phase2. Browse to Troubleshooting → Monitor → KB article | Dashboard insights are AI-generated natural language. No `<Hard Code>` prefix anywhere on the dashboard |
| 2 | Stop the server (Ctrl+C) | Server stops |
| 3 | Edit `.env`: change `AI_MODE=phase2` to `AI_MODE=phase1` | File saved |
| 4 | Restart server: `uvicorn app.main:app --reload --port 8000` | Server restarts |
| 5 | Browse the same path: Troubleshooting → Monitor → KB article | Dashboard insights now show `<Hard Code>` prefix on all insight text (Segment, Intent, Sentiment insights) |
| 6 | Open the chat and type "My monitor is flickering" | Response starts with `<Hard Code>` — keyword-matched hardcoded reply |
| 7 | Check server console | No errors related to the mode switch. Server runs normally |

---

## TC-038: Switch from Phase 1 to Phase 2
**Category:** L. AI_MODE Toggle
**Precondition:** .env has AI_MODE=phase1
**AI_MODE:** phase1 → phase2

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Start server with AI_MODE=phase1. Browse around | All `<Hard Code>` prefixes visible in dashboard insights |
| 2 | Stop server. Edit `.env`: change to `AI_MODE=phase2` (ensure valid ANTHROPIC_API_KEY). Restart server | Server starts successfully |
| 3 | Browse to Troubleshooting → Monitor → KB article | Dashboard insights are now AI-generated — no `<Hard Code>` prefix. Text is contextual and descriptive |
| 4 | Open chat and send a message | Response is AI-generated, contextual, no `<Hard Code>` prefix |

---

## M. Phase 2 Fallback Resilience

---

## TC-039: Fallback on Invalid API Key
**Category:** M. Fallback Resilience
**Precondition:** .env has AI_MODE=phase2 but ANTHROPIC_API_KEY set to `invalid-key-12345`
**AI_MODE:** phase2 (degraded)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Start the server with the invalid API key | Server starts without error — config loads but API key is invalid |
| 2 | Open the app and browse to Troubleshooting → Monitor → KB article | Dashboard still updates! But insights now show `<Hard Code>` prefixes (Phase 1 fallback activated) |
| 3 | Check the server console (terminal) | Should show: `[WARNING] LLM fallback: using Phase 1 rules (reason: ...)` with an authentication error message |
| 4 | Open the chat and type "Help with my monitor" | Response should be the Phase 1 hardcoded keyword match: `<Hard Code> I understand you're experiencing display issues...` |
| 5 | Check console again | Should show: `[WARNING] Chat LLM fallback: ...` with error details |
| 6 | Verify the app does NOT crash | Continue browsing — every page navigation should trigger fallback gracefully. Dashboard keeps updating with Phase 1 output |

---

## TC-040: Fallback on Empty API Key
**Category:** M. Fallback Resilience
**Precondition:** .env has AI_MODE=phase2 but ANTHROPIC_API_KEY= (empty)
**AI_MODE:** phase2 (degraded)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Start the server | Server starts — no crash |
| 2 | Browse the app | Dashboard updates with `<Hard Code>` fallback text. Console shows fallback warnings |
| 3 | Send a chat message | Response is the Phase 1 hardcoded fallback |

---

## N. Full Demo Walkthrough (The 8-Minute Script)

---

## TC-041: Full Demo — Phase 1 Mode
**Category:** N. Full Demo
**Precondition:** Fresh server start. AI_MODE=phase1 in .env. Browser at 1280px+ width.
**AI_MODE:** phase1

| Step | Action | Expected Result |
|------|--------|-----------------|
| | **Scene 1: Anonymous Visitor (2 min)** | |
| 1 | Open `http://localhost:8000` | Split screen loads. Right pane: NBA = 🟢 PASSIVE, Segment = NEW_VISITOR (blue badge), Sentiment = 😐 NEUTRAL, Propensity = GENERAL_BROWSING 100% |
| 2 | Click "Home" → browse product category cards | Dashboard: GENERAL_BROWSING still dominant. Timeline: node(s) appear |
| 3 | Click on "Gaming Laptops" category | PURCHASE_SIGNAL appears in gauge. Timeline grows |
| 4 | Click "Troubleshooting" in nav | TROUBLESHOOTING intent jumps in the gauge. Timeline adds blue node |
| 5 | Click "Monitor" sub-category | TROUBLESHOOTING rises further |
| 6 | Click "Screen Flickering Fix" KB article | TROUBLESHOOTING dominant (70%+). Intent card shows "TROUBLESHOOTING". Insight: `<Hard Code> Customer is focused on troubleshooting content...` |
| | **Scene 2: Login & Profile Merge (1 min)** | |
| 7 | Click "Sign In" → enter `sarah.chen@email.com` / `demo123` → Login | Page refreshes. Nav shows "Sarah Chen" |
| 8 | Check Customer Vitals | 👤 Sarah Chen, ⭐ Gold, 💰 $3,249.97 |
| 9 | Check Segment card | AT_RISK (orange badge) — open case + recurrent issue |
| 10 | Check Historical Sessions | Table shows 2 sessions. ⚠️ RECURRENT ISSUE badge pulsing in red |
| 11 | Check NBA card | Should now be 🚨 CRITICAL (AT_RISK + TROUBLESHOOTING >50% triggers CRITICAL). Red border, pulse animation |
| | **Scene 3: Logged-In Auto-Population (1 min)** | |
| 12 | Click "Warranty Check" | Auto-displays: GX-7500 (❌ Expired, red badge) + TX-1000 (✅ Active, green badge). No serial number entry needed |
| 13 | Click "Case Status" | Auto-displays: CASE-2025-0312 (✅ Resolved, green) + CASE-2026-0891 (🔴 Open, red) |
| 14 | Click the open case to expand | Interaction log visible: 2 entries. Linked case reference to CASE-2025-0312 |
| | **Scene 4: Deepening Concern (2 min)** | |
| 15 | Navigate: Troubleshooting → Monitor → Screen Flickering Fix | TROUBLESHOOTING climbs further. Timeline grows |
| 16 | Wait ~15 seconds on the article | Dwell time accumulates |
| 17 | Navigate away and come back to the same article (3rd visit to same page) | Sentiment shifts to 😕 CONFUSED. Console: `⚠️ Revisit #3...`. Insight: `<Hard Code> Navigation loops detected...` |
| | **Scene 5: Frustration & Critical NBA (1 min)** | |
| 18 | Rage click (3+ rapid clicks on same area) | Sentiment → 😤 FRUSTRATED (red). Console: `🤬 RAGE CLICK DETECTED!` |
| 19 | Check NBA card | 🚨 CRITICAL, red border, pulse. Action: `<Hard Code> Proactive Outreach Recommended...` |
| 20 | Wait ~1 second | Chat widget auto-opens with proactive system message |
| | **Scene 6: Chat & Escalation (1 min)** | |
| 21 | Type "My monitor keeps flickering" in chat | Response: `<Hard Code> I understand you're experiencing display issues...` |
| 22 | Click "Connect Now" to escalate | Chat header changes to "Live Support". Telegram notification fires to operator |
| 23 | (Optional) Reply from Telegram | Reply appears in web chat with live agent indicator |

---

## TC-042: Full Demo — Phase 2 Mode
**Category:** N. Full Demo
**Precondition:** Fresh server start. AI_MODE=phase2 with valid ANTHROPIC_API_KEY in .env.
**AI_MODE:** phase2

| Step | Action | Expected Result |
|------|--------|-----------------|
| | **Scene 1: Anonymous Visitor (2 min)** | |
| 1 | Open `http://localhost:8000` | Same layout as Phase 1. Right pane defaults identical: NBA = PASSIVE, Segment = NEW_VISITOR, Sentiment = NEUTRAL |
| 2 | Click Home → Gaming Laptops → Troubleshooting → Monitor → Screen Flickering Fix | Dashboard updates in real-time. Key difference: insight text is AI-generated natural language (no `<Hard Code>` prefix). Insights are contextual, mentioning the specific pages visited |
| 3 | Check all three insight texts (Segment, Intent, Sentiment) | All should be 1-2 sentence natural language explanations. None should contain `<Hard Code>` |
| | **Scene 2: Login & Profile Merge (1 min)** | |
| 4 | Login as Sarah Chen | Vitals populate. Segment → AT_RISK. History shows 2 sessions + ⚠️ RECURRENT ISSUE badge |
| 5 | Check Segment insight text | AI should reference Sarah's specific situation: open case, recurring visits, Gold tier. No `<Hard Code>` prefix |
| | **Scene 3: Logged-In Auto-Population (1 min)** | |
| 6 | Navigate to Warranty Check and Case Status | Same auto-population as Phase 1 (pages are unchanged). Devices, warranties, and cases display identically |
| | **Scene 4: Deepening Concern (2 min)** | |
| 7 | Navigate troubleshooting pages, revisit KB article 3+ times | TROUBLESHOOTING climbs. On revisit: sentiment shifts to CONFUSED. AI insight should mention the revisit pattern specifically |
| | **Scene 5: Frustration & Critical NBA (1 min)** | |
| 8 | Rage click | Sentiment → FRUSTRATED. NBA → CRITICAL. AI NBA action text should be contextual (e.g., "recurring monitor issue", "expired warranty") rather than generic |
| 9 | Chat auto-opens | Proactive message appears |
| | **Scene 6: Chat & Escalation (1 min)** | |
| 10 | Type "My monitor keeps flickering" | AI response references customer data — e.g., "I can see your GX-7500 has had this issue before" or "your open case CASE-2026-0891". No `<Hard Code>` prefix |
| 11 | Type "I need to speak to someone, this isn't getting resolved" | AI detects escalation intent. `escalation_required` triggers. Telegram notification fires |

---

## O. Edge Cases

---

## TC-043: Logout Resets Session
**Category:** O. Edge Cases
**Precondition:** Logged in as Sarah Chen with browsing history
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Verify dashboard shows Sarah's profile, AT_RISK segment, history table | Logged-in state confirmed |
| 2 | Click "Logout" (or Sign Out button) | Page reloads/updates |
| 3 | Check nav bar | Shows "Sign In" again (no longer "Sarah Chen") |
| 4 | Check Customer Vitals | Back to "Anonymous Visitor" with "?" avatar |
| 5 | Check Segment card | Should reset to "NEW_VISITOR" (blue badge) |
| 6 | Check Historical Sessions | Hidden again — shows "Login to view history" |
| 7 | Check Warranty page | Should show only the search form (no auto-populated devices) |

---

## TC-044: Rapid Navigation Does Not Crash the App
**Category:** O. Edge Cases
**Precondition:** Fresh session
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Rapidly click through 5+ pages in under 3 seconds: Home → Troubleshooting → Monitor → KB article → Warranty → Case Status | All pages load. Dashboard updates for each. No JavaScript errors in console. No server errors |
| 2 | Check Sentiment after rapid navigation | May show FRUSTRATED (rapid switching can trigger frustration signals) or high CONFUSED if pages were revisited |
| 3 | Check the Journey Timeline | Should show a node for each page visited, in correct order |

---

## TC-045: Empty Chat Message
**Category:** O. Edge Cases
**Precondition:** Chat open
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open the chat widget | Chat window visible |
| 2 | Click send without typing anything | Nothing should happen — no empty message sent, no error. The input field should remain focused |
| 3 | Close the chat | Chat closes normally, no errors |

---

## TC-046: Page Refresh Mid-Session
**Category:** O. Edge Cases
**Precondition:** Active session with some browsing history and/or logged in
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Browse several pages to build up session state | Dashboard shows intent scores, timeline nodes, etc. |
| 2 | Press F5 (full page refresh) | Page reloads. Session should persist via cookie |
| 3 | Check the dashboard | Session state should be maintained: same session_id, customer login status preserved. Intent scores may be present from prior events. Note: the `chat_triggered` flag resets on full page load (by design, allowing the demo to be rerun) |
| 4 | If logged in, verify login persists | Nav still shows "Sarah Chen". Customer Vitals still populated |

---

## TC-047: Double-Click Login Button
**Category:** O. Edge Cases
**Precondition:** Not logged in, login form visible
**AI_MODE:** both

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Enter valid credentials (sarah.chen@email.com / demo123) | Credentials entered |
| 2 | Double-click the login/submit button rapidly | Login should succeed once. No duplicate session creation. No error messages. Dashboard shows Sarah's profile normally |

---

## TC-048: Phase 2 Debounce — Rapid Events Don't Overwhelm API
**Category:** O. Edge Cases
**Precondition:** AI_MODE=phase2 with valid API key. Server console visible
**AI_MODE:** phase2

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate through 5 pages rapidly (within 2-3 seconds) | Dashboard updates for each page |
| 2 | Check the server console | The LLM classification should NOT be called for every single event. The debounce logic (2-second minimum interval) should result in at most 1-2 API calls, not 5. Intermediate events use cached results |
| 3 | Wait 3 seconds after the last navigation, then navigate to one more page | A fresh LLM call should fire (>2 seconds since last call). Console may show the API call being made |
| 4 | Perform a rage click during the debounce period | Rage click should bypass the debounce and trigger an immediate LLM call (rage_click events always trigger fresh classification) |

---

## Summary: Test Case Index

| TC | Title | Category | AI_MODE |
|----|-------|----------|---------|
| TC-001 | App Loads with Correct Default State | A. Dashboard Defaults | both |
| TC-002 | All Five Dashboard Sections Render | A. Dashboard Defaults | both |
| TC-003 | Purchase Signal Intent Rises on Product Browsing | B. Intent Accumulation | both |
| TC-004 | Troubleshooting Intent Climbs Step by Step | B. Intent Accumulation | both |
| TC-005 | Warranty Inquiry Intent Rises | B. Intent Accumulation | both |
| TC-006 | Case Follow-Up Intent Rises | B. Intent Accumulation | both |
| TC-007 | General Browsing Baseline Never Dominates | B. Intent Accumulation | both |
| TC-008 | Default Sentiment is NEUTRAL | C. Sentiment Lifecycle | both |
| TC-009 | Steady Dwell Triggers POSITIVE Sentiment | C. Sentiment Lifecycle | both |
| TC-010 | Page Revisits Trigger CONFUSED Sentiment | C. Sentiment Lifecycle | both |
| TC-011 | Rage Clicks Trigger FRUSTRATED and Cooldown | C. Sentiment Lifecycle | both |
| TC-012 | Rage Click Detection Mechanics | D. Rage Click | both |
| TC-013 | NBA Starts as PASSIVE | E. NBA Transitions | both |
| TC-014 | NBA Transitions to OPPORTUNITY | E. NBA Transitions | both |
| TC-015 | NBA Transitions to CRITICAL via FRUSTRATED | E. NBA Transitions | both |
| TC-016 | NBA to CRITICAL via AT_RISK + Troubleshooting | E. NBA Transitions | both |
| TC-017 | CRITICAL Overrides OPPORTUNITY Priority | E. NBA Transitions | both |
| TC-018 | Manual Chat Open and Close | F. Chat Widget | both |
| TC-019 | Chat Auto-Opens on CRITICAL NBA | F. Chat Widget | both |
| TC-020 | Chat Auto-Open Fires Only Once | F. Chat Widget | both |
| TC-021 | Phase 1 Chat — Warranty Keyword | G. Chat Responses | phase1 |
| TC-022 | Phase 1 Chat — Monitor Keyword | G. Chat Responses | phase1 |
| TC-023 | Phase 1 Chat — Purchase Keyword | G. Chat Responses | phase1 |
| TC-024 | Phase 1 Chat — Default Fallback | G. Chat Responses | phase1 |
| TC-025 | Phase 1 Chat — Escalation Keyword | G. Chat Responses | phase1 |
| TC-026 | Phase 2 Chat — Contextual AI Responses | G. Chat Responses | phase2 |
| TC-027 | Phase 2 Chat — Indirect Escalation | G. Chat Responses | phase2 |
| TC-028 | Phase 2 Chat — No Hard Code Prefix | G. Chat Responses | phase2 |
| TC-029 | Login with Valid Credentials | H. Login | both |
| TC-030 | Login with Invalid Credentials | H. Login | both |
| TC-031 | Warranty Check — Logged In Auto-Display | I. Logged-In Pages | both |
| TC-032 | Case Status — Logged In Auto-Display | I. Logged-In Pages | both |
| TC-033 | Timeline Nodes Appear on Navigation | J. Timeline | both |
| TC-034 | Timeline Node Colors by Page Category | J. Timeline | both |
| TC-035 | Timeline Horizontal Scroll | J. Timeline | both |
| TC-036 | Telegram Escalation via Chat | K. Telegram | both |
| TC-037 | Switch from Phase 2 to Phase 1 | L. Toggle | phase2→1 |
| TC-038 | Switch from Phase 1 to Phase 2 | L. Toggle | phase1→2 |
| TC-039 | Fallback on Invalid API Key | M. Fallback | phase2 |
| TC-040 | Fallback on Empty API Key | M. Fallback | phase2 |
| TC-041 | Full Demo — Phase 1 Mode | N. Demo | phase1 |
| TC-042 | Full Demo — Phase 2 Mode | N. Demo | phase2 |
| TC-043 | Logout Resets Session | O. Edge Cases | both |
| TC-044 | Rapid Navigation Stress Test | O. Edge Cases | both |
| TC-045 | Empty Chat Message | O. Edge Cases | both |
| TC-046 | Page Refresh Mid-Session | O. Edge Cases | both |
| TC-047 | Double-Click Login Button | O. Edge Cases | both |
| TC-048 | Phase 2 Debounce | O. Edge Cases | phase2 |
