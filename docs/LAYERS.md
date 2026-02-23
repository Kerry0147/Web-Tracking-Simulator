# Project ECHO — Build Layers
## Layered Code Generation Roadmap for Claude Code

### How to Use This File
1. Work through layers **in order** (Layer 1 → 2 → 3 → ... → 7)
2. For each layer, paste the **Claude Code Prompt** into your Claude Code session in VS Code
3. **Test** using the verification steps before moving to the next layer
4. If a layer fails testing, fix it before proceeding — later layers depend on earlier ones

### Project Root Structure
```
Web CEC Simulator/
├── docs/
│   ├── PRD.md          ← You are here (spec reference)
│   └── LAYERS.md       ← This file (build roadmap)
├── app/
├── static/
├── templates/
├── requirements.txt
├── .env
└── README.md
```

---

## Layer 1: Data Foundation
**Goal:** Define all data models and load mock data. Everything else builds on this.

### PRD Sections to Read
- Section 6 (Mock Data Design) — all subsections
- Section 5.1 (Read Skills) — understand what data the skills need to return
- Section 3.2 C (Live Categorization) — enum definitions for Segment, Intent, Sentiment

### Files to Generate
```
app/
├── __init__.py
├── models.py           # Pydantic models for all data types
└── data/
    ├── __init__.py
    └── mock_data.json   # Complete mock dataset
```

### Claude Code Prompt
```
Read docs/PRD.md sections 6 (Mock Data Design) and 3.2 C (Live Categorization — enum definitions).

Generate Layer 1: Data Foundation.

Create app/models.py with Pydantic models:
- Enums: Segment (VIP, AT_RISK, NEW_VISITOR, RETURNING, DORMANT), Intent (TROUBLESHOOTING, WARRANTY_INQUIRY, CASE_FOLLOW_UP, PURCHASE_SIGNAL, GENERAL_BROWSING), Sentiment (POSITIVE, NEUTRAL, CAUTIOUS, CONFUSED, FRUSTRATED), NBAState (PASSIVE, OPPORTUNITY, CRITICAL)
- Models: Customer, Device, Warranty, Case, InteractionLog, HistoricalSession, KBArticle, Product, LoginCredentials
- Models: BehaviorEvent, SessionState, ClassificationResult, NBAResult
- All models should have proper type hints and default values

Create app/data/mock_data.json with the COMPLETE dataset per PRD Section 6:
- Sarah Chen customer profile (all fields from 6.1)
- 2 devices with full specs (6.3)
- 2 warranty records (linked to devices)
- 2 support cases with interaction logs (6.4)
- 2 historical sessions with page detail arrays (6.5)
- 8 products across 4 categories with full specs (6.6 — gaming_laptops, workstations, office_laptops, tablets — 2 each)
- 12 KB articles (3 each for audio, monitor, keyboard, battery) with complete step-by-step content
- Login credentials

Important: Every entity must be linked via IDs per the Data Relationship Map in 6.2. Use the exact IDs specified in the PRD (CUST-2024-0847, DEV-GX7500-A1847, etc).

Also create app/__init__.py and app/data/__init__.py (empty).
```

### Test
```bash
cd project-echo
python -c "
import json
from app.models import Customer, Device, Warranty, Case, Segment, Intent, Sentiment

# Load mock data
with open('app/data/mock_data.json') as f:
    data = json.load(f)

# Validate customer
c = Customer(**data['customer'])
print(f'Customer: {c.name}, Tier: {c.tier}')

# Validate devices
for d in data['devices']:
    dev = Device(**d)
    print(f'Device: {dev.product_name}, SN: {dev.serial_number}')

# Validate linkage
assert data['devices'][0]['customer_id'] == data['customer']['id']
assert data['warranties'][0]['device_id'] == data['devices'][0]['id']
assert data['cases'][0]['device_id'] == data['devices'][0]['id']

# Validate enums
print(f'Segments: {[s.value for s in Segment]}')
print(f'Intents: {[i.value for i in Intent]}')
print(f'Sentiments: {[s.value for s in Sentiment]}')

# Validate KB articles
total_kb = sum(len(articles) for articles in data['kb_articles'].values())
print(f'KB articles: {total_kb} (expected 12)')

# Validate products
total_products = sum(len(prods) for prods in data['products'].values())
print(f'Products: {total_products} (expected 8)')

print('\\nLayer 1 PASSED')
"
```

### Done When
- [ ] All Pydantic models validate without errors
- [ ] mock_data.json loads and deserializes correctly
- [ ] All entity IDs match the PRD relationship map
- [ ] 12 KB articles, 8 products, 2 devices, 2 warranties, 2 cases, 2 sessions present

---

## Layer 2: Static UI Shell
**Goal:** Get the split-screen layout rendering with navigation. No dynamic behavior yet — just the visual skeleton.

### PRD Sections to Read
- Section 2 (UI Design — Split-Screen Console)
- Section 3.1.1 (Product Domain)
- Section 3.1.2 (Navigation Structure)
- Section 3.1.4 (Identity State — for the login button placement)
- Section 7.1 (Technology Stack)

### Files to Generate
```
app/
├── main.py               # FastAPI app with basic routes
requirements.txt
templates/
├── base.html             # Split-screen layout shell (left 60%, right 40%)
├── left/
│   └── home.html         # Home page with product category cards
├── right/
│   └── dashboard.html    # Dashboard layout with placeholder sections (A–E)
└── components/
    └── nav.html          # Top navigation bar (ProBook logo, nav items, login button)
static/
├── css/
│   └── styles.css        # Tailwind CDN + custom split-screen styles
└── js/
    └── app.js            # Minimal JS (page navigation handler)
```

### Claude Code Prompt
```
Read docs/PRD.md sections 2 (UI Design), 3.1.1-3.1.2 (Navigation), 3.1.4 (Identity State), and 7.1 (Tech Stack).

Existing files: app/models.py, app/data/mock_data.json (Layer 1).

Generate Layer 2: Static UI Shell.

Create requirements.txt with: fastapi, uvicorn[standard], jinja2, python-multipart, sse-starlette, httpx, python-dotenv

Create app/main.py:
- FastAPI app with Jinja2 templates
- Load mock_data.json into memory at startup
- Routes: GET / (home), GET /troubleshooting, GET /warranty, GET /case-status
- Each route renders the split-screen layout with the appropriate left pane content
- Right pane always renders dashboard.html with placeholder sections

Create templates/base.html:
- Full-page split-screen: left pane 60% width, right pane 40% width
- Include Tailwind CSS via CDN (https://cdn.tailwindcss.com)
- Include HTMX via CDN (https://unpkg.com/htmx.org)
- Left pane has: navigation bar (via nav.html include) + content area (block)
- Right pane has: dashboard sections A through E as placeholder cards
- Divider line between panes

Create templates/components/nav.html:
- "ProBook" logo text on the left
- Nav items: Home | Troubleshooting | Warranty Check | Case Status
- Active nav item highlighted
- Login button top-right: shows "Sign In" with 🔑 icon when logged out

Create templates/left/home.html:
- Hero banner: "ProBook — Performance Meets Innovation"
- 4 product category cards in a 2x2 grid: Gaming Laptops 🎮, Workstations 💻, Office Laptops 📁, Tablets 📱
- Each card shows category name, tagline, product count, and "Explore →" link

Create templates/right/dashboard.html:
- 5 stacked sections with placeholder content:
  A. 🎯 Next Best Action — card with green "Monitor Behavior" default
  B. 👤 Customer Vitals — card showing "Anonymous Visitor" + empty propensity gauge
  C. 🧠 Live Categorization — 3 sub-cards: Segment, Intent, Sentiment with default values
  D. 🗺️ Journey Timeline — empty horizontal track with "Waiting for activity..." text
  E. 📅 Historical Sessions — hidden by default (shows "Login to view history")
- Use a dark/neutral sidebar style so it visually contrasts with the bright customer portal

Style: Professional, clean. Left pane = light background (customer-facing). Right pane = dark/navy background (agent dashboard feel).
```

### Test
```bash
cd project-echo
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# Open http://localhost:8000 in browser
# Verify:
# - Split screen renders (left 60%, right 40%)
# - Navigation bar shows with all 4 items + login button
# - Home page shows 4 product category cards
# - Right pane shows 5 placeholder dashboard sections
# - Clicking nav items loads different left pane content (even if pages are minimal)
```

### Done When
- [ ] Split-screen layout renders at 1280px+ width
- [ ] Navigation bar has ProBook logo, 4 nav items, login button (top-right)
- [ ] Home page displays 4 product category cards
- [ ] Right pane shows all 5 dashboard section placeholders
- [ ] Visual contrast between left pane (light) and right pane (dark)

---

## Layer 3: Left Pane Content Pages
**Goal:** Build all customer portal pages with full content depth. Still no live tracking — but all clickable content exists.

### PRD Sections to Read
- Section 3.1.2 (Navigation Structure — page depth details)
- Section 3.1.3 (Knowledge Base Structure)
- Section 3.1.4 (Identity State)
- Section 3.1.5 (Logged-In Page Enhancements — warranty + case auto-display)
- Section 6 (Mock Data — for content to display)

### Files to Generate
```
templates/left/
├── home.html                  # UPDATE: add product detail sub-pages
├── troubleshooting.html       # Category menu (Audio, Monitor, Keyboard, Battery)
├── troubleshooting_list.html  # Article list for a specific category
├── kb_article.html            # Full KB article page
├── warranty.html              # Dual-mode: guest search form + logged-in auto-display
├── case_status.html           # Dual-mode: guest search form + logged-in auto-display
└── product_detail.html        # Product category listing (2 products per category)
templates/components/
├── login_modal.html           # Login overlay/modal
app/
├── main.py                    # UPDATE: add routes for sub-pages, login/logout, data lookups
```

### Claude Code Prompt
```
Read docs/PRD.md sections 3.1.2 through 3.1.5 (all left pane specs) and Section 6 (Mock Data).

Existing files: app/models.py, app/data/mock_data.json (Layer 1), app/main.py, all Layer 2 templates.

Generate Layer 3: Left Pane Content Pages.

UPDATE app/main.py to add these routes:
- GET /products/{category} — show 2 products for the selected category
- GET /troubleshooting — category menu (4 cards: Audio, Monitor, Keyboard, Battery)
- GET /troubleshooting/{category} — article list for that category (3 articles)
- GET /troubleshooting/{category}/{article_id} — full KB article with steps
- GET /warranty — dual-mode page (see below)
- GET /case-status — dual-mode page (see below)
- POST /login — validate credentials against mock data, set session state
- POST /logout — clear session state
- All routes should pass session state (logged_in, customer_id) to templates

WARRANTY CHECK (per PRD 3.1.5):
- Guest: shows a serial number search form + POST /api/warranty-lookup endpoint
- Logged in: auto-displays all devices registered to customer with warranty cards (green/red badges), PLUS the search form below

CASE STATUS (per PRD 3.1.5):
- Guest: shows a case number search form + POST /api/case-lookup endpoint
- Logged in: auto-displays all cases filed by customer with status badges, expandable detail cards, linked case references, PLUS the search form below

LOGIN:
- Create templates/components/login_modal.html — a modal overlay with email + password fields
- On successful login (match against mock_data.json login credentials), set session cookie/state
- Navigation bar updates to show "👤 Sarah Chen" instead of "Sign In"
- On logout, clear session and revert

TROUBLESHOOTING sub-pages:
- templates/left/troubleshooting.html — 4 category cards with icons (🔊 Audio, 🖥️ Monitor, ⌨️ Keyboard, 🔋 Battery) and article count
- templates/left/troubleshooting_list.html — breadcrumb (Troubleshooting > Monitor) + list of 3 articles with title, difficulty badge, est. time
- templates/left/kb_article.html — breadcrumb + title + difficulty + time + numbered steps + "Was this helpful?" buttons + related articles

PRODUCTS:
- templates/left/product_detail.html — breadcrumb + 2 product cards per category showing name, tagline, specs, price, stock status

Use HTMX for page transitions so navigation feels seamless (hx-get + hx-target on the left pane content area).
```

### Test
```bash
# Start server: uvicorn app.main:app --reload --port 8000
# In browser:
# 1. Click all 4 nav items — each loads correct content
# 2. Click Home > Gaming Laptops > see GX-7500 and GX-8000
# 3. Click Troubleshooting > Monitor > Screen Flickering Fix — see full KB article
# 4. Click Warranty Check — see search form (guest mode)
# 5. Click Sign In — enter sarah.chen@email.com / demo123
# 6. Nav bar changes to show "Sarah Chen"
# 7. Navigate to Warranty Check — see 2 device cards auto-displayed (GX-7500 EXPIRED, TX-1000 ACTIVE)
# 8. Navigate to Case Status — see 2 case cards (CASE-2025-0312 resolved, CASE-2026-0891 open)
# 9. Click the open case card — expands to show details + linked case reference
# 10. Logout — reverts to guest mode
```

### Done When
- [ ] All 4 nav sections load content correctly
- [ ] Troubleshooting has 3 levels: menu → article list → KB article (12 total articles)
- [ ] Product pages show 2 products per category (8 total)
- [ ] Login/logout works with session state
- [ ] Warranty Check auto-populates with 2 devices when logged in
- [ ] Case Status auto-populates with 2 cases when logged in
- [ ] Guest mode shows search forms only (no auto-populate)

---

## Layer 4: Behavioral Tracking
**Goal:** Capture user interactions on the left pane and accumulate them on the backend. No dashboard updates yet — just the data pipeline.

### PRD Sections to Read
- Section 4 (Behavioral Tracking System — entire section)
- Section 4.1 (Tracked Events)
- Section 4.2 (Intent Score Accumulation — point system + normalization)
- Section 4.3 (Sentiment Detection Thresholds)

### Files to Generate
```
static/js/
├── behavior.js              # Client-side event tracking
app/engine/
├── __init__.py
├── behavior_tracker.py      # Server-side session state accumulator
├── session_manager.py       # Manages active sessions
app/
├── main.py                  # UPDATE: add POST /api/track-event endpoint
```

### Claude Code Prompt
```
Read docs/PRD.md section 4 (Behavioral Tracking System) in full — pay close attention to 4.1 (events), 4.2 (point accumulation + normalization formula), and 4.3 (sentiment thresholds).

Existing files: all Layer 1-3 files.

Generate Layer 4: Behavioral Tracking.

Create static/js/behavior.js:
- Track these events and send to POST /api/track-event:
  - page_view: sent on every page navigation (HTMX afterSwap event)
  - page_leave: sent on navigation away, includes dwell_seconds (time since last page_view)
  - click: sent on click of any element with [data-track] attribute
  - rage_click: detect 3+ clicks on same element within 2 seconds → send rage_click event
  - scroll: track scroll percentage and speed on pages with scrollable content
  - form_submit: capture warranty search and case search form submissions
  - login / logout: sent when session state changes
- All events include: { type, page, timestamp, ...event_specific_data }
- Dwell time tracking: record page start time, calculate dwell on navigation away

Create app/engine/session_manager.py:
- SessionManager class that stores active sessions in a dict (keyed by session_id from cookie)
- Methods: create_session(), get_session(), update_session(), get_or_create()
- Each session stores: session_id, customer_id (null if guest), events list, start_time

Create app/engine/behavior_tracker.py:
- BehaviorTracker class that processes incoming events and accumulates state
- Maintains per-session: page_visit_history, dwell_times, raw_intent_scores, sentiment_signals
- Intent scoring per PRD 4.2: each action adds POINTS (not percentages) to the relevant intent
- get_normalized_intents() method: returns dict of {intent: percentage} where all sum to 100%
- Sentiment tracking per PRD 4.3: accumulate signal weights, return highest-weight sentiment
- FRUSTRATED overrides all other sentiments regardless of weight
- Rage click detection (server-side backup): verify rage_click events from client
- Page revisit tracking: count how many times each page is visited in this session

UPDATE app/main.py:
- Add POST /api/track-event endpoint that receives behavior events
- Create session on first request (via cookie)
- Pass events to BehaviorTracker
- Add GET /api/session-state endpoint (debug) that returns current session state as JSON

Include app/engine/__init__.py.
```

### Test
```bash
# Start server: uvicorn app.main:app --reload --port 8000
# In browser:
# 1. Open browser console (F12)
# 2. Navigate around the left pane — check console for event sends
# 3. Click rapidly on same element — verify rage_click event fires
# 4. Visit Troubleshooting > Monitor > KB article — dwell 10+ seconds — navigate away
# 5. Open http://localhost:8000/api/session-state in new tab:
#    - Verify page_visit_history includes the pages visited
#    - Verify intent scores show TROUBLESHOOTING with points accumulated
#    - Verify dwell times recorded
# 6. Login as Sarah, visit more pages, check session-state again:
#    - Verify customer_id is now populated
#    - Verify intent scores updated
```

### Done When
- [ ] behavior.js sends events to backend for all tracked event types
- [ ] Rage click detection works (3+ clicks in 2s on same element)
- [ ] Dwell time is calculated correctly per page
- [ ] /api/session-state returns accumulated intent scores (raw points)
- [ ] get_normalized_intents() returns percentages summing to 100%
- [ ] Sentiment signals accumulate correctly (page revisits → CONFUSED, rage clicks → FRUSTRATED)
- [ ] Session persists across page navigations (cookie-based)

---

## Layer 5: Classification Engine
**Goal:** Build the rule-based classifier and NBA engine that evaluates accumulated behavior and returns the full classification result.

### PRD Sections to Read
- Section 3.2 A (Next Best Action — trigger conditions)
- Section 3.2 C (Live Categorization — segment assignment rules, intent, sentiment)
- Section 4.2 (Intent Score Accumulation — the rules to implement)
- Section 4.3 (Sentiment Detection Thresholds — the rules to implement)
- Section 5.2 (Routing Skills — classify_behavior output schema)

### Files to Generate
```
app/engine/
├── classifier.py           # classify_behavior — returns enums + insights
├── nba_engine.py           # Next Best Action decision logic
app/skills/
├── __init__.py
├── read_skills.py          # get_customer_profile, check_warranty_status, get_customer_history
└── routing_skills.py       # classify_behavior wrapper
```

### Claude Code Prompt
```
Read docs/PRD.md sections 3.2 A (NBA), 3.2 C (Categorization — ALL enum tables with assignment rules), 4.2-4.3 (scoring rules), and 5.1-5.2 (Skills).

Existing files: all Layer 1-4 files, especially app/engine/behavior_tracker.py and app/models.py.

Generate Layer 5: Classification Engine.

Create app/engine/classifier.py:
- classify_behavior(session_state, customer_data=None) function
- Takes BehaviorTracker accumulated state + optional customer data (if logged in)
- Returns ClassificationResult (from models.py) containing:
  - segment: Segment enum — use assignment rules from PRD 3.2 C (priority: AT_RISK > VIP > DORMANT > RETURNING > NEW_VISITOR)
  - intent_scores: dict of {Intent: float_percentage} — normalized from raw points
  - primary_intent: Intent enum (highest scoring)
  - sentiment: Sentiment enum — from behavioral signals per PRD 4.3
  - insights: dict of {segment_insight, intent_insight, sentiment_insight} — hardcoded strings prefixed with "<Hard Code>"
- Segment logic:
  - If guest (no customer_data): NEW_VISITOR
  - If customer has open unresolved case OR same primary intent in ≥3 sessions in 30 days: AT_RISK
  - If customer tier Gold/Platinum AND LTV > 2000: VIP
  - If customer last visit > 90 days ago: DORMANT
  - If customer has previous sessions: RETURNING
  - Else: NEW_VISITOR
- Insight text examples (hardcoded):
  - AT_RISK segment: "<Hard Code> Customer has visited for the same issue 3 times in 30 days. Open case remains unresolved. Elevated attention recommended."
  - TROUBLESHOOTING intent at >70%: "<Hard Code> Customer is focused on troubleshooting content. Repeated visits to monitor-related KB articles suggest an unresolved technical issue."
  - FRUSTRATED sentiment: "<Hard Code> Behavioral signals indicate difficulty — rapid page switching and repeated page revisits suggest the customer is not finding what they need."

Create app/engine/nba_engine.py:
- determine_nba(classification_result) function
- Returns NBAResult with: state (PASSIVE/OPPORTUNITY/CRITICAL), action_text, should_trigger_chat
- Rules per PRD 3.2 A:
  - CRITICAL: sentiment == FRUSTRATED OR (segment == AT_RISK AND primary intent TROUBLESHOOTING > 50%)
  - OPPORTUNITY: primary intent TROUBLESHOOTING > 60% AND sentiment != FRUSTRATED
  - PASSIVE: default
- Priority: CRITICAL > OPPORTUNITY > PASSIVE
- action_text: hardcoded per state, prefixed with "<Hard Code>"
- should_trigger_chat: True only for CRITICAL

Create app/skills/read_skills.py:
- get_customer_profile(customer_id, mock_data) → Customer + Devices
- check_warranty_status(identifier, mock_data) → list of Warranty records (by customer_id returns all, by serial returns one)
- get_customer_history(customer_id, mock_data) → HistoricalSessions + Cases

Create app/skills/routing_skills.py:
- classify_behavior_skill(session_state, mock_data, customer_id=None) — wrapper that loads customer data via read_skills if logged in, then calls classifier.py

Include app/skills/__init__.py.
```

### Test
```bash
# Start server and run test:
python -c "
from app.engine.behavior_tracker import BehaviorTracker
from app.engine.classifier import classify_behavior
from app.engine.nba_engine import determine_nba
from app.models import Segment, Intent, Sentiment, NBAState
import json

with open('app/data/mock_data.json') as f:
    mock_data = json.load(f)

# Simulate Sarah's session: troubleshooting + frustrated
tracker = BehaviorTracker()
tracker.process_event({'type': 'page_view', 'page': '/troubleshooting'})
tracker.process_event({'type': 'page_view', 'page': '/troubleshooting/monitor'})
tracker.process_event({'type': 'page_view', 'page': '/troubleshooting/monitor/KB-MON-001'})
tracker.process_event({'type': 'page_leave', 'page': '/troubleshooting/monitor/KB-MON-001', 'dwell_seconds': 45})
tracker.process_event({'type': 'rage_click', 'element': 'nav-link', 'click_count': 5})

# Classify with customer data (logged in as Sarah)
result = classify_behavior(tracker.get_state(), customer_data=mock_data)
print(f'Segment: {result.segment}')  # Should be AT_RISK
print(f'Primary Intent: {result.primary_intent}')  # Should be TROUBLESHOOTING
print(f'Sentiment: {result.sentiment}')  # Should be FRUSTRATED
print(f'Intent scores: {result.intent_scores}')  # TROUBLESHOOTING should be highest

# NBA
nba = determine_nba(result)
print(f'NBA State: {nba.state}')  # Should be CRITICAL
print(f'Trigger chat: {nba.should_trigger_chat}')  # Should be True
print(f'Action: {nba.action_text}')  # Should contain <Hard Code>

print('\\nLayer 5 PASSED')
"
```

### Done When
- [ ] Classifier returns correct Segment based on customer data + rules
- [ ] Intent scores normalize to 100% correctly
- [ ] Sentiment returns FRUSTRATED when rage clicks detected
- [ ] NBA returns CRITICAL when frustrated + at-risk
- [ ] NBA returns OPPORTUNITY when troubleshooting >60% + not frustrated
- [ ] NBA returns PASSIVE as default
- [ ] All insight text starts with `<Hard Code>`
- [ ] Read skills return correct mock data

---

## Layer 6: Live Dashboard
**Goal:** Wire everything together — behavioral events update the right pane in real-time via SSE.

### PRD Sections to Read
- Section 3.2 (Right Pane — all subsections A through E)
- Section 7.2 (Data Flow)
- Section 7.3 (SSE Event Types)

### Files to Generate
```
app/
├── main.py                    # UPDATE: add SSE endpoint, wire tracking → classification → SSE push
templates/right/
├── dashboard.html             # UPDATE: add SSE listeners with hx-ext="sse"
├── partials/
│   ├── nba_card.html          # 🎯 Next Best Action partial
│   ├── vitals.html            # 👤 Customer Vitals + 📊 Propensity Gauge partial
│   ├── categorization.html    # 🧠 Segment + Intent + Sentiment cards partial
│   ├── timeline.html          # 🗺️ Journey Timeline partial
│   └── history.html           # 📅 Historical Sessions table partial
```

### Claude Code Prompt
```
Read docs/PRD.md sections 3.2 (entire Right Pane spec — all subsections A through E with icons and visual specs) and 7.2-7.3 (Data Flow + SSE Events).

Existing files: all Layer 1-5 files.

Generate Layer 6: Live Dashboard.

UPDATE app/main.py:
- Add GET /api/dashboard-stream SSE endpoint using sse-starlette
- After each POST /api/track-event, run classify_behavior and determine_nba
- Push updated HTML partials via SSE events:
  - Event "nba-update" → renders nba_card.html partial
  - Event "vitals-update" → renders vitals.html partial
  - Event "categorization-update" → renders categorization.html partial
  - Event "timeline-update" → renders timeline.html partial
  - Event "history-update" → renders history.html partial (only on login event)

UPDATE templates/right/dashboard.html:
- Add hx-ext="sse" with sse-connect="/api/dashboard-stream"
- Each section has sse-swap targeting the correct event name
- Sections are stacked vertically in a scrollable dark-themed sidebar

Create templates/right/partials/nba_card.html:
- Card with colored border/header matching state (green/yellow/red)
- Icon (👁️/💡/🚨) + state label + descriptive insight text
- Smooth transition animation on state change

Create templates/right/partials/vitals.html:
- If guest: "Anonymous Visitor" with minimal info
- If logged in: profile fields with icons (👤 Name, 📆 Since, ⭐ Tier, 💰 LTV, 📋 Cases, 📅 Last Contact)
- Propensity Gauge: horizontal multi-bar chart showing all 5 intents ordered by percentage
  - Each bar: icon + label + colored bar (width proportional to %) + percentage text
  - Use Tailwind utility classes for bar widths (e.g., w-[72%])
  - Colors: TROUBLESHOOTING=blue, WARRANTY=purple, CASE=orange, PURCHASE=green, BROWSING=gray

Create templates/right/partials/categorization.html:
- Three cards side by side (or stacked if narrow):
  - 🏷️ Segment card: icon + enum badge + colored tag + insight text
  - 🎯 Intent card: icon + primary intent label + insight text
  - 😀 Sentiment card: emoji + enum label + colored indicator + insight text
- Each insight text is in a lighter/muted font below the enum badge

Create templates/right/partials/timeline.html:
- Horizontal scrollable container
- Connected dots (circles) with lines between them, left to right
- Each node: category label on top, detail + dwell time below
- Node color matches sentiment at that point (green/red/amber)
- New nodes append to the right end
- If empty: "Waiting for activity..." placeholder

Create templates/right/partials/history.html:
- If not logged in: "Login to view session history" message
- If logged in: table with columns per PRD 3.2 E (Date/Time, Pages, Intent, Sentiment, Insight)
- Show data from historical_sessions in mock data
- If RECURRENT ISSUE detected: ⚠️ alert badge above the table with explanation
- Recurrence rule: same primary intent in ≥3 sessions (2 historical + current) in 30 days

Styling: Right pane uses a dark navy/slate background (#1a2332 or similar). Cards have subtle borders and slight shadow. Text is light/white. Enum badges are colored pills. Transitions should be smooth.
```

### Test
```bash
# Start server: uvicorn app.main:app --reload --port 8000
# In browser:
# 1. Open app — right pane shows default state (Passive, Anonymous, Neutral)
# 2. Click Troubleshooting — right pane updates: TROUBLESHOOTING intent rises in gauge
# 3. Click Monitor > KB article — intent climbs higher, timeline node appears
# 4. Navigate back and revisit same page — sentiment shifts to CONFUSED
# 5. Login as Sarah — vitals populate, historical sessions appear, ⚠️ RECURRENT ISSUE shows
# 6. Navigate rapidly with clicks — sentiment shifts to FRUSTRATED, NBA goes CRITICAL
# 7. Verify all 5 sections update independently
# 8. Verify timeline shows connected dots with correct labels
```

### Done When
- [ ] SSE connection established on page load
- [ ] All 5 dashboard sections update in real-time as user navigates
- [ ] NBA transitions: Passive → Opportunity → Critical correctly
- [ ] Propensity gauge shows multi-bar with correct percentages
- [ ] Categorization shows correct enums with insight text (all `<Hard Code>` prefixed)
- [ ] Timeline renders horizontal connected dots with page details
- [ ] Historical sessions table appears on login with ⚠️ RECURRENT ISSUE badge
- [ ] Dark-themed dashboard styling looks professional

---

## Layer 7: Chat Widget & Telegram Escalation
**Goal:** Add the chat widget with hardcoded responses and Telegram escalation.

### PRD Sections to Read
- Section 3.1.6 (Chat Widget)
- Section 5.3 (Action Skills — escalate_to_human)
- Section 7.4 (Telegram Escalation Flow)

### Files to Generate
```
app/chat/
├── __init__.py
├── handler.py               # Chat message router (hardcoded Phase 1)
├── telegram_bridge.py       # Telegram Bot API integration
static/js/
├── chat.js                  # Chat widget UI logic
templates/components/
├── chat_widget.html         # Chat widget HTML
app/
├── main.py                  # UPDATE: add chat endpoints
.env.example                 # Template for environment variables
```

### Claude Code Prompt
```
Read docs/PRD.md sections 3.1.6 (Chat Widget), 5.3 (Action Skills), and 7.4 (Telegram Escalation Flow).

Existing files: all Layer 1-6 files.

Generate Layer 7: Chat Widget & Telegram Escalation.

Create templates/components/chat_widget.html:
- Floating button bottom-right of left pane: "💬 Need Help?" pill
- Click to expand into chat window (overlays on left pane)
- Chat window: header with "🤖 AI Assistant" label, message area, input field, send button
- "Transfer to Live Agent" button in header
- When NBA triggers auto-open: chat opens with a pre-filled system message
- Mode indicator: "🤖 AI Assistant" or "👤 Live Agent" in header

Create static/js/chat.js:
- Toggle chat open/close
- Send messages via POST /api/chat/send
- Receive responses (poll or SSE)
- Handle "Transfer to Agent" button click
- Auto-open when triggered by NBA engine (listen for SSE event)

Create app/chat/handler.py:
- handle_message(message, session_state, customer_data) function
- Phase 1: returns hardcoded responses prefixed with "<Hard Code>" based on keywords:
  - If message mentions "warranty" or "expired": "<Hard Code> I can see you're asking about warranty coverage. Let me look into your account details."
  - If message mentions "flickering" or "monitor": "<Hard Code> I understand you're experiencing display issues. Based on your account, I can see this has been an ongoing concern."
  - If message mentions "agent" or "human" or "transfer": trigger escalation
  - Default: "<Hard Code> Thank you for reaching out. How can I assist you today?"

Create app/chat/telegram_bridge.py:
- send_escalation(token, chat_id, context) async function
  - Formats message: "🚨 ESCALATION\n👤 {name} ({tier})\n📋 {issue}\n🔧 Warranty: {status}\n😤 Sentiment: {sentiment}\n📊 Visit #{count} in 30 days"
  - Sends via Telegram Bot API POST
- poll_for_reply(token, chat_id) — polls for operator's response
- Relay operator response back to web chat

UPDATE app/main.py:
- POST /api/chat/send — receives message, returns response from handler
- POST /api/chat/escalate — triggers Telegram notification
- SSE event "chat-auto-open" — sent when NBA goes CRITICAL with should_trigger_chat=True

Create .env.example:
- TELEGRAM_BOT_TOKEN=your_token_here
- TELEGRAM_CHAT_ID=your_chat_id_here
- ANTHROPIC_API_KEY=your_key_here  # Phase 2
```

### Test
```bash
# 1. Set up .env with your actual Telegram bot token and chat ID
# 2. Start server: uvicorn app.main:app --reload --port 8000
# In browser:
# 3. Click "💬 Need Help?" — chat opens
# 4. Type "My monitor keeps flickering" — get hardcoded response
# 5. Type "Can I talk to a human?" — response should mention transfer
# 6. Click "Transfer to Live Agent" — check Telegram for notification
# 7. Reply from Telegram — verify message appears in web chat
# 8. Chat header should change to "👤 Live Agent"
# 9. Navigate left pane to trigger CRITICAL NBA — chat should auto-open
```

### Done When
- [ ] Chat widget opens/closes on button click
- [ ] Messages send and receive hardcoded responses (all `<Hard Code>` prefixed)
- [ ] "Transfer to Live Agent" sends Telegram notification with full context
- [ ] Telegram reply relays back to web chat
- [ ] Chat label changes from "🤖 AI Assistant" to "👤 Live Agent" on escalation
- [ ] NBA CRITICAL auto-opens chat with proactive message
- [ ] .env.example documents all required environment variables

---

## Final Integration Test

After all 7 layers are complete, run through the **Demo Walkthrough Script** (PRD Section 8):

| Scene | Duration | Key Test |
|-------|----------|----------|
| 1. Anonymous Visitor | 2 min | Dashboard shows defaults; intent scores change on navigation |
| 2. Login & Profile Merge | 1 min | Vitals populate; historical sessions appear; ⚠️ RECURRENT ISSUE |
| 3. Logged-In Auto-Population | 1 min | Warranty + Case Status auto-display Sarah's data |
| 4. Deepening Concern | 2 min | Intent climbs; sentiment shifts on page revisit |
| 5. Frustration & Critical NBA | 1 min | Rage clicks → FRUSTRATED → CRITICAL NBA → chat auto-opens |
| 6. Chat & Escalation | 1 min | Chat works; Telegram escalation fires |

**Total: ~8 minutes**

If the full walkthrough completes without errors, **Phase 1 is done** ✅

---

## Quick Reference: File → Layer Map

| File | Layer | Purpose |
|------|-------|---------|
| `app/models.py` | 1 | All Pydantic models + enums |
| `app/data/mock_data.json` | 1 | Complete mock dataset |
| `app/main.py` | 2→3→4→6→7 | FastAPI app (updated each layer) |
| `requirements.txt` | 2 | Python dependencies |
| `templates/base.html` | 2 | Split-screen layout shell |
| `templates/components/nav.html` | 2 | Navigation bar |
| `templates/left/home.html` | 2→3 | Home page |
| `templates/left/troubleshooting*.html` | 3 | Troubleshooting pages |
| `templates/left/kb_article.html` | 3 | KB article page |
| `templates/left/warranty.html` | 3 | Warranty check (dual-mode) |
| `templates/left/case_status.html` | 3 | Case status (dual-mode) |
| `templates/left/product_detail.html` | 3 | Product listing |
| `templates/components/login_modal.html` | 3 | Login modal |
| `static/js/behavior.js` | 4 | Client-side event tracking |
| `app/engine/behavior_tracker.py` | 4 | Server-side event accumulation |
| `app/engine/session_manager.py` | 4 | Session management |
| `app/engine/classifier.py` | 5 | Rule-based classification |
| `app/engine/nba_engine.py` | 5 | Next Best Action logic |
| `app/skills/read_skills.py` | 5 | Mock data retrieval skills |
| `app/skills/routing_skills.py` | 5 | classify_behavior wrapper |
| `templates/right/dashboard.html` | 6 | Dashboard layout with SSE |
| `templates/right/partials/*.html` | 6 | All 5 dashboard section partials |
| `static/js/chat.js` | 7 | Chat widget logic |
| `templates/components/chat_widget.html` | 7 | Chat widget HTML |
| `app/chat/handler.py` | 7 | Hardcoded chat responses |
| `app/chat/telegram_bridge.py` | 7 | Telegram Bot API integration |
| `.env.example` | 7 | Environment variable template |
