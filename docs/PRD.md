# Project ECHO — PRD v2.1 (Machine-Readable)
## Customer Journey Tracking PoC

| Field | Value |
|-------|-------|
| Version | 2.1 (Implementation Ready — Post-Alignment Review) |
| Date | February 11, 2026 |
| Status | Approved for Code Generation |
| Phase | Phase 1 — Hardcoded AI outputs marked with `<Hard Code>` for Phase 2 replacement |
| Audience | Business Leadership (Go / No-Go Decision) |
| Tech Stack | Python (FastAPI) + HTMX + Tailwind CSS + SSE |
| Product Domain | ProBook — Consumer Electronics (Laptops & Tablets) |

---

## 1. Executive Summary

### 1.1 Objective
Build a **"Glass Box" Proof of Concept (PoC)** that demonstrates real-time Customer Engagement Center (CEC) capabilities. The system mimics a high-end Predictive Engagement platform, showing how AI analyzes customer behavior on a website to predict intent, assign segments, and trigger proactive actions.

### 1.2 Key Differentiator
A **Split-Screen Console** showing "Cause and Effect." As the user interacts with the mock customer portal (Left Pane), the Agent Dashboard (Right Pane) updates instantly with AI-driven insights. This makes the invisible visible — business leadership can see exactly how behavioral signals translate into actionable intelligence.

### 1.3 Phase Strategy

| Phase | Scope | AI Approach |
|-------|-------|-------------|
| Phase 1 (Current) | Full UI + behavioral tracking + hardcoded AI outputs | All AI-generated text prefixed with `<Hard Code>`. Classification and scoring are rule-based (Section 4). Agent Skills return mock data. |
| Phase 2 (Future) | Replace hardcoded outputs with Claude API calls | Real-time Claude API for insights, chat, classification, and recommendations. Rule engine (Section 4) replaced by `classify_behavior` skill (Section 5.2). |

### 1.4 Industry Context
This PoC is modeled after industry-leading Predictive Engagement platforms such as Genesys Predictive Engagement, which uses machine learning, dynamic segmentation, and real-time outcome scoring to identify the right moments for proactive customer engagement. The approach of pre-defining segments and outcomes as standardized categories, then using AI to score probabilities against those categories in real-time, is the established industry pattern.

---

## 2. User Interface Design: The Split-Screen Console

The application is a single-page web app divided vertically into two panes within one browser tab. The panes communicate via Server-Sent Events (SSE) — when the user acts on the left, the right updates in real-time.

| Pane | Width | Purpose |
|------|-------|---------|
| Left Pane | 60% | Customer Portal — Simulates the ProBook support website |
| Right Pane | 40% | Live Analysis Dashboard — Agent/supervisor view showing real-time AI insights |

**Target display:** Desktop only (1280px+ width). No responsive/mobile layout required for PoC.

---

## 3. Functional Requirements

### 3.1 Left Pane: Customer Portal (ProBook Electronics)

#### 3.1.1 Product Domain
The mock website represents **ProBook**, a consumer electronics brand. Product line:
- 🎮 Gaming Laptops (GX-7500 Pro, GX-8000 Ultra)
- 💻 Workstations (WS-5000, WS-6000 Pro)
- 📁 Office Laptops (OL-3000, OL-3500 Slim)
- 📱 Tablets (TX-1000, TX-2000 Pro)

Each product has full specs, pricing, and stock status defined in mock data.

#### 3.1.2 Navigation Structure
Top navigation bar with logo and menu items. Multi-level page depth for meaningful journey tracking.

| Nav Item | Page Depth | Description |
|----------|-----------|-------------|
| 🏠 Home | 1 level → Product categories → Product detail | Landing page with product category cards (Gaming, Workstation, Office, Tablet). Each card links to category listing showing 2 products with specs. |
| 🔧 Troubleshooting | 3 levels → Category menu → Article list → KB article | Sub-categories: Audio, Monitor, Keyboard, Battery. Each has 3 KB articles with step-by-step guides. |
| 🛡️ Warranty Check | 1 level → Auto-display + Form | Guest: serial number search form only. Logged in: auto-displays all registered devices with warranty status, plus search form for additional lookups. See 3.1.5. |
| 📋 Case Status | 1 level → Auto-display + Form | Guest: case number search form only. Logged in: auto-displays all cases filed by this customer with status and history, plus search form. See 3.1.5. |

#### 3.1.3 Knowledge Base Structure
12 total KB articles across 4 troubleshooting categories:

| Category | Articles | Topics |
|----------|----------|--------|
| 🔊 Audio | 3 articles | No Sound After Update \| Bluetooth Audio Crackling \| Microphone Not Detected |
| 🖥️ Monitor | 3 articles | Screen Flickering Fix \| External Monitor Not Detected \| Resolution & Scaling Guide |
| ⌨️ Keyboard | 3 articles | Keys Not Responding \| Backlight Not Working \| Function Key Reference |
| 🔋 Battery | 3 articles | Fast Battery Drain \| Not Charging When Plugged In \| Battery Health & Cycle Count |

#### 3.1.4 Identity State
**Login button** positioned top-right of the navigation bar (standard web placement).

| State | Behavior | Dashboard Impact |
|-------|----------|-----------------|
| 👤 Guest (default) | Full browsing access. Behavioral tracking active for current session only. No data persisted to DB. Warranty Check and Case Status show search forms only. | All dashboard sections active except Historical Sessions. Profile shows "Anonymous Visitor." |
| 🔑 Logged In | Full browsing access. Session linked to customer record. Behavior persisted. Warranty Check auto-shows all registered devices + warranty status. Case Status auto-shows all filed cases. | Full dashboard. Customer Vitals show profile. Historical Sessions table appears with past visit data. |

**Demo credentials:** `sarah.chen@email.com` / `demo123`

#### 3.1.5 Logged-In Page Enhancements
When a customer is logged in, the system automatically retrieves all data associated with their customer ID and pre-populates the relevant pages.

**🛡️ Warranty Check Page (Logged In):**
- **Auto-display:** All devices registered to the customer are listed in a card layout, each showing: device name, serial number, purchase date, warranty type, warranty status (Active/Expired), and days remaining or days since expiry.
- **Visual indicators:** ✅ Green badge for Active warranty, ❌ Red badge for Expired warranty.
- **Extended warranty upsell:** If a warranty is expired or nearing expiry, display an "Extended Warranty Available" banner with pricing.
- **Additional lookup:** Search form still available below the auto-display section for looking up other serial numbers.
- **Skill triggered:** `get_customer_profile` → returns device list → `check_warranty_status` for each device

**📋 Case Status Page (Logged In):**
- **Auto-display:** All support cases filed by the customer are listed, showing: case ID, subject, device name, status badge (Open/Resolved), creation date, and last update date.
- **Visual indicators:** 🔴 Red badge for Open cases, ✅ Green badge for Resolved cases.
- **Expandable detail:** Clicking a case card expands to show full details: description, resolution (if resolved), interaction log, linked cases, and internal notes.
- **Linked cases:** If a case references a previous case (e.g., CASE-2026-0891 links to CASE-2025-0312), display a "Linked Case" reference the customer can click to view.
- **Additional lookup:** Search form still available below for looking up cases by case number directly.
- **Skill triggered:** `get_customer_history` → returns all cases with interaction logs

> **Demo impact:** When Sarah logs in and navigates to Warranty Check, she immediately sees both her devices — the GX-7500 Gaming Laptop (warranty EXPIRED, red badge) and the TX-1000 Tablet (warranty ACTIVE, green badge). No serial number needed. When she visits Case Status, she sees her open case (CASE-2026-0891, red badge) and resolved case (CASE-2025-0312, green badge) with full history.

#### 3.1.6 Chat Widget
Floating chat button at bottom-right of the left pane. Labeled "💬 Need Help?"
- **Manual trigger:** Customer clicks the chat button to open
- **Auto trigger:** NBA engine can open the chat proactively when Critical state is reached
- **Phase 1:** Hardcoded bot responses prefixed with `<Hard Code>`
- **Phase 2:** Claude-powered conversational agent using Agent Skills (read tools)
- **Escalation:** "Transfer to Live Agent" button sends Telegram notification to operator. Operator responds from phone, message relayed back to web chat. Chat label changes from "🤖 AI Assistant" to "👤 Live Agent."

---

### 3.2 Right Pane: Live Analysis Dashboard

Layout is identical for guest and logged-in users, with two exceptions: (1) Customer Vitals show profile data only when logged in, and (2) Historical Sessions section appears only when logged in. All sections update independently via SSE.

**Dashboard Sections (top to bottom):**

| # | Section | Icon | Purpose |
|---|---------|------|---------|
| A | Next Best Action | 🎯 | Tells the agent exactly what to do right now |
| B | Customer Vitals & Propensity Gauge | 👤 📊 | Who is this customer + what are they likely trying to do |
| C | Live Categorization | 🧠 | AI classification: Segment + Intent + Sentiment with insights |
| D | Journey Timeline | 🗺️ | Visual path of pages visited in this session |
| E | Historical Sessions | 📅 | Past visit records with recurrence detection (logged-in only) |

#### 🎯 A. Next Best Action (Fixed Top)
Single recommendation displayed at the top of the dashboard. Always visible. Only one NBA shown at a time, determined by priority.

| State | Icon | Display Label | Trigger Condition | Color |
|-------|------|---------------|-------------------|-------|
| Passive | 👁️ | Monitor Behavior | Default state — no triggers met | Green 🟢 |
| Opportunity | 💡 | Suggest Self-Service Resources | Intent = TROUBLESHOOTING at >60% AND Sentiment ≠ FRUSTRATED | Yellow 🟡 |
| Critical | 🚨 | Proactive Outreach Recommended | Sentiment = FRUSTRATED OR (Segment = AT_RISK AND Intent = TROUBLESHOOTING at >50%) | Red 🔴 |

**Priority:** Critical > Opportunity > Passive.

Each NBA state includes a descriptive insight text (hardcoded in Phase 1) explaining the reasoning. Language should be measured and informative, not alarmist.

#### 👤 B. Customer Vitals & 📊 Propensity Gauge

**Profile fields** (displayed when logged in):

| Field | Icon | Example Value |
|-------|------|---------------|
| Name | 👤 | Sarah Chen |
| Customer Since | 📆 | December 2024 |
| Tier | ⭐ | Gold |
| Lifetime Value | 💰 | $3,249.97 |
| Open Cases | 📋 | 1 |
| Last Contact Date | 📅 | January 22, 2026 |

**📊 Propensity Gauge:** Multi-bar chart showing all detected intents ranked by probability (highest first). Each bar shows the intent label, a visual bar, and percentage.

Example display:
- 🔧 TROUBLESHOOTING ████░ 72%
- 🛡️ WARRANTY_INQUIRY ██░░░ 18%
- 👁️ GENERAL_BROWSING █░░░░ 7%
- 🛒 PURCHASE_SIGNAL ░░░░░ 3%

#### 🧠 C. Live Categorization (Hybrid Model)
Three classification dimensions displayed as cards. Each card has a **standardized enum label** (for machine logic) plus a **free-text AI insight** (for human comprehension). The enum drives trigger rules; the insight makes the demo impressive.

> **Design Decision:** Standardized enums were chosen over free-form AI naming because: (1) deterministic triggers require reliable category matching, (2) industry platforms like Genesys require pre-defined segments and outcomes, and (3) the Glass Box concept demands consistent labels for the audience to follow cause-and-effect logic.

**🏷️ Segment Enums:**

| Enum | Icon | Label | Assignment Rule | Color |
|------|------|-------|-----------------|-------|
| `VIP` | 💎 | VIP Customer | Tier = Gold/Platinum AND LTV > $2,000 | Purple |
| `AT_RISK` | ⚠️ | At-Risk | Open unresolved case OR same intent ≥3 sessions in 30 days | Orange |
| `NEW_VISITOR` | 🆕 | New Visitor | No customer record (guest) OR first session | Blue |
| `RETURNING` | 🔁 | Returning | Has previous sessions, no risk signals | Green |
| `DORMANT` | 💤 | Dormant | Last visit > 90 days ago | Gray |

**Priority:** AT_RISK > VIP > DORMANT > RETURNING > NEW_VISITOR

**🎯 Intent Enums:**

| Enum | Icon | Label | Primary Signals |
|------|------|-------|-----------------|
| `TROUBLESHOOTING` | 🔧 | Troubleshooting | Visited Troubleshooting section; viewed KB article with dwell > 10s |
| `WARRANTY_INQUIRY` | 🛡️ | Warranty Check | Visited Warranty page; entered serial number or viewed device warranty |
| `CASE_FOLLOW_UP` | 📋 | Case Follow-Up | Visited Case Status page; viewed existing case or searched by case number |
| `PURCHASE_SIGNAL` | 🛒 | Purchase Interest | Viewed product pages with dwell > 30s; visited multiple categories |
| `GENERAL_BROWSING` | 👁️ | General Browsing | No strong signal — default state |

**😀 Sentiment Enums (Behavioral):**
Sentiment is derived entirely from behavioral signals — not text analysis.

| Enum | Icon | Label | Behavioral Signals | Color |
|------|------|-------|--------------------|-------|
| `POSITIVE` | 😊 | Engaged | Steady dwell (10–60s); linear navigation; no revisits | Green |
| `NEUTRAL` | 😐 | Browsing | Short dwell (3–10s); casual pattern; no friction | Gray |
| `CAUTIOUS` | 🤔 | Attentive | Moderate dwell on specific pages; revisiting 1–2 pages | Amber |
| `CONFUSED` | 😕 | Needs Guidance | Same page 2+ times; back-and-forth navigation | Yellow |
| `FRUSTRATED` | 😤 | Experiencing Difficulty | Rage clicks (3+ in 2s); rapid page switching (<3s for 3+ pages); excessive scroll oscillation | Red |

#### 🗺️ D. Journey Timeline (Subway Map)
Horizontal connected-dot timeline. Nodes appear left-to-right as the customer navigates pages.
- 🏷️ **Node top label:** Page category (e.g., Troubleshooting, Warranty Check)
- 🔍 **Node detail:** Specific page + dwell time (e.g., "Monitor > Flickering Fix — 4m 20s")
- 🎨 **Node color:** 🟢 Green = positive/neutral; 🔴 Red = frustrated/confused; 🟠 Amber = cautious
- ➖ **Connections:** Lines connecting all dots in sequence
- ⏰ **No timestamps required** — left-to-right ordering provides sufficient sequence information
- ↔️ **Scrollable:** Horizontal scroll when nodes exceed visible area

#### 📅 E. Historical Sessions (Logged-In Only)
Table showing the customer's past visits. Appears only when logged in.

**📝 Table Columns:**

| Column | Icon | Data | Purpose |
|--------|------|------|---------|
| Date/Time | 📅 | Session date and start time | When the customer visited |
| Pages Clicked | 📊 | Count of distinct pages visited | Session depth / engagement |
| Intent | 🎯 | Primary intent enum for that session | What they were trying to do |
| Sentiment | 😀 | Final sentiment enum for that session | How they felt |
| Insight | 💡 | AI-generated summary noting repeat pages and patterns | Pattern recognition across sessions |

> **⚠️ Recurrence Detection:** If the same primary Intent appears in 3 or more sessions within the last 30 days, display a "⚠️ RECURRENT ISSUE" alert badge above the table. This is a key demo moment.

---

## 4. Behavioral Tracking System (Phase 1: Rule-Based Engine)

> **❗ Phase Scope Notice:** This entire section describes the Phase 1 rule-based implementation. All intent scoring, sentiment detection, and threshold logic are deterministic rules executed in Python. In Phase 2, this rule engine is replaced by the `classify_behavior` Agent Skill (Section 5.2), which sends raw behavioral event data to the Claude API. See also Section 9 (Phase 2 Replacement Map).

Client-side JavaScript (`behavior.js`) captures user interactions and sends events to the backend. The backend accumulates these signals to compute intent scores and sentiment.

### 4.1 Tracked Events

| Event | Data Captured | Use |
|-------|--------------|-----|
| `page_view` | Page path, timestamp | Journey timeline; intent scoring |
| `page_leave` | Page path, dwell time in seconds | Dwell-based intent scoring; sentiment analysis |
| `click` | Element clicked, page context | Click frequency; engagement depth |
| `rage_click` | Element, click count, window (ms) | Frustration detection → sentiment |
| `scroll` | Page, scroll percentage, speed (fast/normal/slow) | Content engagement; frustration (oscillating scroll) |
| `form_submit` | Form ID, submitted data | Warranty lookup; case search intent |
| `chat_open` | Trigger type (manual / auto-NBA) | Tracks proactive engagement effectiveness |
| `login` | Customer ID | Profile merge; historical session load; auto-populate pages |

### 4.2 Intent Score Accumulation

**How scoring works:** Each user action adds weighted **points** (not percentages) to the relevant intent category. Points accumulate without an upper limit. At display time, all raw point totals are **normalized** so that all intents sum to exactly 100%.

**Normalization Formula:**
```
displayed_percentage(intent) = raw_points(intent) / sum(all_raw_points) × 100%
```

**Example:** Sarah visits Troubleshooting (+15 pts), clicks Monitor sub-category (+10 pts), opens KB article (+20 pts), dwells 15s on article (+10 pts). Meanwhile, each page visit adds +3 pts to GENERAL_BROWSING (4 pages = 12 pts). Raw totals: TROUBLESHOOTING = 55, GENERAL_BROWSING = 12, total = 67. Displayed: TROUBLESHOOTING = 55/67 = 82%, GENERAL_BROWSING = 12/67 = 18%.

**Point Accumulation Table:**

| User Action | Intent Affected | Points Added |
|-------------|----------------|--------------|
| Visit Troubleshooting menu | `TROUBLESHOOTING` | +15 pts |
| Click Troubleshooting sub-category | `TROUBLESHOOTING` | +10 pts |
| Open KB article | `TROUBLESHOOTING` | +20 pts |
| Dwell on KB article > 10s | `TROUBLESHOOTING` | +10 pts |
| Visit Warranty Check page | `WARRANTY_INQUIRY` | +25 pts |
| Enter serial number / view device warranty | `WARRANTY_INQUIRY` | +30 pts |
| Visit Case Status page | `CASE_FOLLOW_UP` | +25 pts |
| Search for case number / view case detail | `CASE_FOLLOW_UP` | +30 pts |
| Browse product categories on Home page | `PURCHASE_SIGNAL` | +5 pts |
| View specific product detail page | `PURCHASE_SIGNAL` | +15 pts |
| Dwell on product page > 30s | `PURCHASE_SIGNAL` | +15 pts |
| View multiple products in sequence | `PURCHASE_SIGNAL` | +10 pts |
| Any page visit (baseline) | `GENERAL_BROWSING` | +3 pts |

### 4.3 Sentiment Detection Thresholds
Sentiment is computed from behavioral signals. Each signal has a weight; the sentiment with the highest accumulated weight wins. FRUSTRATED signals override all others regardless of weight.

| Signal | Detection Rule | Sentiment | Weight |
|--------|---------------|-----------|--------|
| Rage click | 3+ clicks on same area within 2 seconds | 😤 FRUSTRATED | 40 |
| Rapid page switch | 3+ pages visited with <3s dwell each | 😤 FRUSTRATED | 30 |
| Page revisit | Same page visited 2+ times in session | 😕 CONFUSED | 20 |
| Back-and-forth | A→B→A navigation pattern detected | 😕 CONFUSED | 15 |
| Extended dwell | Single page dwell > 60 seconds | 🤔 CAUTIOUS | 10 |
| Steady browsing | 3+ pages with 10–60s dwell each | 😊 POSITIVE | 10 |
| No signals | Default when nothing else detected | 😐 NEUTRAL | 0 |

---

## 5. Agent Skills Architecture
Skills define the actions the system can take. In Phase 1, these are function calls returning mock data. In Phase 2, they become Claude API tools.

### 5.1 Read Skills (Data Retrieval)

| Skill | Input | Returns | Used By |
|-------|-------|---------|---------|
| `get_customer_profile` | customer_id | Full profile: name, tier, LTV, registered devices (with serial numbers), contact info | Customer Vitals panel; Warranty Check auto-display; chat agent context |
| `check_warranty_status` | customer_id OR serial_number | All warranty records for the customer (when logged in) or specific warranty for a serial number (guest lookup) | Warranty Check page; chat agent |
| `get_customer_history` | customer_id | Historical sessions, all filed cases with interaction logs, linked cases | Historical Sessions table; Case Status auto-display; recurrence detection |

### 5.2 Routing Skills (Classification)

| Skill | Input | Returns |
|-------|-------|---------|
| `classify_behavior` | Session state: accumulated events, dwell times, click patterns, page sequence, scroll data, rage click events | JSON: `{ segment: enum, intent: {scores_object}, sentiment: enum, insights: {segment_text, intent_text, sentiment_text}, nba: {state, action_text} }` |

- **Phase 1:** This skill executes the rule-based engine described in Section 4. Deterministic threshold logic.
- **Phase 2:** This skill sends the raw behavioral event stream to the Claude API with a system prompt instructing Claude to return structured JSON using the standardized enums. Replaces the entire Section 4 rule engine.

### 5.3 Action Skills

| Skill | Input | Effect |
|-------|-------|--------|
| `escalate_to_human` | Customer context (name, tier, issue summary, warranty status, sentiment, visit count) | Sends formatted Telegram alert to operator. Changes chat mode from AI to Live Agent. Operator responds via Telegram, relayed to web chat via SSE. |

---

## 6. Mock Data Design
All mock data is stored in a single `mock_data.json` file and loaded into an in-memory Python dictionary at startup. All entities are linked via ID references.

### 6.1 Mock Customer: Sarah Chen

| Field | Value |
|-------|-------|
| Customer ID | `CUST-2024-0847` |
| Name | Sarah Chen |
| Email | sarah.chen@email.com |
| Tier | Gold |
| Customer Since | December 10, 2024 |
| Lifetime Value | $3,249.97 |
| Open Cases | 1 (CASE-2026-0891) |
| Location | Seattle, WA |
| Login Credentials (demo) | sarah.chen@email.com / demo123 |

### 6.2 Data Relationship Map

| Entity | ID | Linked To | Relationship |
|--------|-----|-----------|-------------|
| Customer | `CUST-2024-0847` | — | Root entity — Sarah Chen |
| Device 1 | `DEV-GX7500-A1847` | CUST-2024-0847 | 🎮 Gaming Laptop registered to Sarah |
| Device 2 | `DEV-TX1000-B2201` | CUST-2024-0847 | 📱 Tablet registered to Sarah |
| Warranty 1 | `WRN-2024-0847-01` | DEV-GX7500-A1847 | ❌ Expired warranty for Gaming Laptop (SN: GX7500-2024-A1847) |
| Warranty 2 | `WRN-2025-0847-02` | DEV-TX1000-B2201 | ✅ Active warranty for Tablet (SN: TX1000-2025-B2201) |
| Case 1 | `CASE-2025-0312` | DEV-GX7500-A1847 | ✅ Resolved: Monitor flickering (Aug 2025) |
| Case 2 | `CASE-2026-0891` | DEV-GX7500-A1847 + CASE-2025-0312 | 🔴 Open: Flickering returned (Jan 2026). Links to Case 1. |
| Session 1 | `SESS-2025-0815` | CUST-2024-0847 | First visit for monitor issue → Created Case 1 |
| Session 2 | `SESS-2026-0122` | CUST-2024-0847 | Second visit, frustrated → Created Case 2 |
| Session 3 | (Live demo) | CUST-2024-0847 | Third visit = current demo session → Triggers RECURRENT ISSUE |

### 6.3 Registered Devices

| | Device 1 | Device 2 |
|-|----------|----------|
| Product | 🎮 ProBook GX-7500 Pro Gaming Laptop | 📱 ProBook TX-1000 Tablet |
| Serial Number | GX7500-2024-A1847 | TX1000-2025-B2201 |
| Purchase Date | December 15, 2024 | June 20, 2025 |
| Purchase Price | $2,499.99 | $749.98 |
| Warranty Status | ❌ EXPIRED (Dec 15, 2025) — 57 days past | ✅ ACTIVE — 130 days remaining |
| Extended Warranty | Available: $299.99 for 24 months | Available: $149.99 for 12 months |
| Related Cases | CASE-2025-0312 + CASE-2026-0891 | None |

### 6.4 Support Cases

| | Case 1 | Case 2 |
|-|--------|--------|
| Case ID | CASE-2025-0312 | CASE-2026-0891 |
| Status | ✅ Resolved (Aug 22, 2025) | 🔴 Open (since Jan 22, 2026) |
| Device | GX-7500 Pro (SN: GX7500-2024-A1847) | GX-7500 Pro (SN: GX7500-2024-A1847) |
| Subject | Monitor flickering during gaming | Monitor flickering returned — same issue |
| Resolution | Driver update + refresh rate reduced to 165Hz | Pending — hardware fault suspected |
| Interactions | 3 (chat, email, email) | 2 (chat, email) |
| Linked Case | None | Links to CASE-2025-0312 |
| Key Note | Customer satisfied (score: 4/5) | Warranty expired. Repair cost: $350–$450. Retention risk. |

### 6.5 Historical Sessions

| | Session 1 | Session 2 |
|-|-----------|-----------|
| Session ID | SESS-2025-0815 | SESS-2026-0122 |
| Date / Time | Aug 15, 2025 — 10:23 AM | Jan 22, 2026 — 2:47 PM |
| Duration | 12 minutes | 18 minutes |
| Pages Visited | 5 | 8 |
| Primary Intent | 🔧 TROUBLESHOOTING (78%) | 🔧 TROUBLESHOOTING (85%) |
| Sentiment | 🤔 CAUTIOUS | 😤 FRUSTRATED |
| Outcome | Created CASE-2025-0312 | Created CASE-2026-0891 |
| Key Insight | Methodical first visit; read KB article for 4m 20s before filing case | Revisited same KB articles with less dwell; checked warranty (expired); showed frustration signals |

> **📖 Sarah's Story Arc:** Gold-tier customer with a recurring monitor flickering issue on her GX-7500 Gaming Laptop (SN: GX7500-2024-A1847). First visit was calm and methodical — she found the KB article, filed a case, and it was resolved with a driver fix. Second visit: the fix stopped working. She re-read the same articles, discovered her warranty expired, and showed frustration. Now on her third visit (the live demo session), the system detects the recurrence pattern, expired warranty, and behavioral frustration — escalating to Critical NBA. The TX-1000 Tablet serves as a contrast: active warranty, no issues.

### 6.6 Additional Mock Data
The `mock_data.json` file also includes:
- Full product catalog (8 products across 4 categories with complete specs and pricing)
- 12 KB articles (3 per troubleshooting category with step-by-step guides)
- Detailed interaction logs for each support case (dates, channel, summary)

---

## 7. Technical Architecture

### 7.1 Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Backend | FastAPI (Python 3.11+) | Native WebSocket/SSE support; async; auto API docs at /docs |
| Frontend | HTMX + Tailwind CSS | Partial page updates via SSE without SPA complexity; rapid styling |
| Real-time | Server-Sent Events (SSE) | One-way server→client push; HTMX native SSE support |
| Data | In-memory dict from `mock_data.json` | No DB setup; instant load; easy demo modification |
| Chat (Phase 1) | Hardcoded responses | Prefixed with `<Hard Code>` |
| Chat (Phase 2) | Claude API + tool use | Conversational agent with read skills as tools |
| Escalation | Telegram Bot API | Alert to operator phone; bidirectional relay |

### 7.2 Data Flow
1. Browser (`behavior.js`) tracks user actions: clicks, dwell time, scroll speed, rage clicks, page visits.
2. Each meaningful action is sent to `POST /api/track-event` on the backend.
3. `behavior_tracker.py` accumulates session state in memory.
4. `classifier.py` (Phase 1 rule engine) evaluates accumulated behavior → returns Segment, Intent scores, Sentiment, Insight text.
5. `nba_engine.py` evaluates classifier output → determines Next Best Action state.
6. Updated HTML partials are pushed via SSE at `/api/dashboard-stream`.
7. HTMX on the right pane swaps the updated partials in real-time.

### 7.3 SSE Event Types

| Event | Triggers Update To |
|-------|--------------------|
| `nba-update` | 🎯 Next Best Action card |
| `vitals-update` | 👤 Customer Vitals + 📊 Propensity Gauge |
| `categorization-update` | 🧠 Segment / Intent / Sentiment panels |
| `timeline-update` | 🗺️ Appends new node to Journey Timeline |
| `history-update` | 📅 Refreshes Historical Sessions table (on login only) |

### 7.4 Telegram Escalation Flow
Prerequisites: Telegram bot already set up. Bot token and chat ID stored in `.env` file.

1. Customer clicks "Transfer to Live Agent" in the chat widget.
2. Backend formats an escalation message with full context: customer name, tier, issue summary, warranty status, sentiment, visit count.
3. Message sent to operator's Telegram via Bot API.
4. Operator reads context and replies via Telegram.
5. Backend relays Telegram response to web chat via SSE.
6. Chat label changes from "🤖 AI Assistant" to "👤 Live Agent."

---

## 8. Demo Walkthrough Script
Target duration: ~8 minutes.

### Scene 1: Anonymous Visitor (2 min)
1. Open the application — split screen loads with dashboard in default state.
2. Right pane shows: NBA = 🟢 Passive, Segment = 🆕 New Visitor, low intent scores, Sentiment = 😐 Neutral.
3. Click Home → browse product categories → right pane: GENERAL_BROWSING rises slightly.
4. Click Troubleshooting → right pane: TROUBLESHOOTING intent jumps.
- 🗣️ *"Even without knowing who this person is, we're already tracking behavioral signals and predicting intent in real-time."*

### Scene 2: Login & Profile Merge (1 min)
1. Click Sign In → enter sarah.chen@email.com / demo123.
2. Right pane transforms: Customer Vitals populate with full profile.
3. Historical Sessions table appears showing 2 past visits.
4. ⚠️ RECURRENT ISSUE badge appears — same intent detected across 3+ sessions.
5. Segment changes from 🆕 NEW_VISITOR → ⚠️ AT_RISK.
- 🗣️ *"The moment the customer logs in, we merge their anonymous session with their full history. The system immediately recognizes this is a recurring problem."*

### Scene 3: Logged-In Page Auto-Population (1 min)
1. Navigate to Warranty Check → page auto-displays both registered devices: GX-7500 (❌ Expired) and TX-1000 (✅ Active). No serial number entry needed.
2. Navigate to Case Status → page auto-displays both cases: CASE-2025-0312 (✅ Resolved) and CASE-2026-0891 (🔴 Open). Click the open case to expand details.
- 🗣️ *"The system knows this customer. No manual lookups needed — her devices, warranty status, and support history are all immediately visible."*

### Scene 4: Deepening Concern (2 min)
1. Navigate: Troubleshooting → Monitor → Screen Flickering Fix article.
2. Right pane: TROUBLESHOOTING intent climbs to ~72%; timeline node appears.
3. Spend ~30 seconds reading, then navigate back to Troubleshooting.
4. Re-visit the same article → Sentiment shifts from 😐 NEUTRAL to 😕 CONFUSED.
- 🗣️ *"The system noticed the customer went back to an article they've already read — in this session and in previous visits. The loop behavior triggers a sentiment shift."*

### Scene 5: Frustration & Critical NBA (1 min)
1. Navigate rapidly between several pages with quick clicks (simulate frustration).
2. Right pane: Sentiment shifts to 😤 FRUSTRATED.
3. NBA card changes to 🚨 Critical: "Proactive Outreach Recommended."
4. Chat widget auto-opens with proactive message.
- 🗣️ *"This is the moment of truth. The system independently determined this customer needs human intervention — before they call in angry or leave altogether."*

### Scene 6: Chat & Escalation (1 min)
1. Open chat → send a message → receive hardcoded response.
2. Click "Transfer to Live Agent" → Telegram notification fires to operator's phone.
- 🗣️ *"In Phase 2, the AI agent has full context — the customer's profile, devices, warranty status, case history, and behavioral analysis — before the human takes over. No repeat explanations needed."*

---

## 9. Phase 2 Replacement Map
Every `<Hard Code>` marker in Phase 1 maps to a specific Claude API call in Phase 2. The Section 4 rule engine is entirely replaced by the `classify_behavior` skill.

| Phase 1 (Hardcoded) | Phase 2 (Claude API) | Implementation |
|---------------------|---------------------|----------------|
| Section 4 rule engine (thresholds, weights, formulas) | `classify_behavior` skill (Section 5.2) calls Claude API | Send raw behavioral events as context; Claude returns structured JSON with enums + reasoning |
| NBA insight text | Claude generates from full session context | System prompt + session state + customer history → 1–2 sentence recommendation |
| Categorization AI Insight text | Claude explains enum selection reasoning | Input: behavioral signals + selected enum → "explain your reasoning" |
| Chat responses | Claude with tool use (read skills) | Tools: get_customer_profile, check_warranty_status, get_customer_history |
| Sentiment insight text | Claude interprets behavioral patterns | Input: scroll/click/dwell data → natural language explanation |
| Historical session insight | Claude summarizes cross-session patterns | Input: all sessions for customer → pattern analysis + recurrence detection |

---

## 10. Definition of Done (Phase 1)

### 10.1 Core Functionality
- [ ] Split-screen layout renders correctly on 1280px+ displays
- [ ] Left pane: all 4 navigation sections functional with multi-level content
- [ ] Left pane: 12 KB articles accessible across 4 troubleshooting categories
- [ ] Left pane: login/logout toggles identity state (top-right button)
- [ ] Left pane: Warranty Check and Case Status forms return correct mock data

### 10.2 Logged-In Page Enhancements
- [ ] Warranty Check auto-displays all registered devices with warranty status on login
- [ ] Case Status auto-displays all filed cases with status badges on login
- [ ] Both pages retain manual search forms for additional lookups
- [ ] Device → Warranty → Case linkage is visually clear and navigable

### 10.3 Live Analysis Dashboard
- [ ] All 5 dashboard sections render and update independently via SSE
- [ ] Next Best Action transitions correctly: 🟢 Passive → 🟡 Opportunity → 🔴 Critical
- [ ] Propensity Gauge shows multi-bar chart with all intents ranked by normalized percentage
- [ ] Live Categorization displays correct enums with icons + descriptive insight text
- [ ] Journey Timeline shows connected horizontal dots with page detail and dwell info
- [ ] Historical Sessions table appears on login with past visit data
- [ ] ⚠️ RECURRENT ISSUE badge triggers when same intent appears ≥3 sessions in 30 days

### 10.4 Behavioral Tracking
- [ ] Page views, dwell time, clicks, and rage clicks captured and sent to backend
- [ ] Intent scores accumulate as weighted points and normalize to 100% for display
- [ ] Sentiment detection responds to rage clicks, rapid page switching, and revisit patterns

### 10.5 Chat & Escalation
- [ ] Chat widget opens manually and via NBA auto-trigger
- [ ] Hardcoded chat responses display with `<Hard Code>` prefix
- [ ] Telegram escalation sends formatted alert with full customer context
- [ ] Operator Telegram replies relay back to web chat

### 10.6 Demo Readiness
- [ ] All `<Hard Code>` markers clearly visible for Phase 2 identification
- [ ] Full demo walkthrough (including auto-populated pages) executable in under 10 minutes
- [ ] Mock data tells coherent Sarah Chen story arc from login through escalation
- [ ] All data entities properly linked: Customer → Devices → Warranties → Cases → Sessions
