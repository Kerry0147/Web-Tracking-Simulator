# Web Tracking Simulator

**A "Glass Box" to track user behavior in web**

It features a unique **Split-Screen Console** that makes the invisible logic of AI-driven customer support visible. As users interact with a simulated portal on the left, an Agent Dashboard on the right instantly updates with AI-driven behavioral analysis, intent prediction, and Next Best Actions (NBA) via Server-Sent Events (SSE).

## ✨ Features

* **Split-Screen Architecture:** A side-by-side view showing cause (customer behavior) and effect (agent insights) in real-time.
* **Behavioral Tracking Engine:** Client-side tracking of page views, dwell time, rapid navigation, and rage clicks to determine customer intent and sentiment.
* **Real-Time AI Categorization:** Dynamic assignment of customer Segments, Intents, and Sentiments (e.g., classifying a user as `FRUSTRATED` when rage clicks are detected).
* **Next Best Action (NBA) Engine:** Automatically transitions from *Passive* to *Opportunity* to *Critical* states based on behavioral thresholds, triggering proactive chat interventions when necessary.
* **Dual-Mode Intelligence (`AI_MODE`):**
    * **Phase 1 (Rule-Based):** A deterministic rule engine that acts as a reliable, lightning-fast fallback.
    * **Phase 2 (LLM-Powered):** Integrates Anthropic's Claude 3.5 Haiku to generate dynamic, natural-language insights and handle conversational chat using tool-use (RAG-style data retrieval).
* **Omnichannel Escalation:** Chat widget seamlessly escalates to a live human operator via a Telegram Bot integration.

## 🛠️ Technology Stack

* **Backend:** Python 3.11+, FastAPI, Uvicorn
* **Frontend:** HTMX, Tailwind CSS, Vanilla JavaScript
* **Real-Time:** Server-Sent Events (SSE) via `sse-starlette`
* **AI Integration:** Anthropic SDK (Claude Haiku 4.5)
* **Data:** In-memory state management with Pydantic models (Zero database setup required)


## 🚀 Getting Started

### Prerequisites
* Python 3.11 or higher
* An Anthropic API Key (for Phase 2 AI mode)
* A Telegram Bot Token (optional, for human escalation testing)

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/web-tracking-simulator.git](https://github.com/yourusername/web-tracking-simulator.git)
   cd web-tracking-simulator.git
  
