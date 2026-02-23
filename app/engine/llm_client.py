import json
import time
from typing import Dict, Optional, Any, Tuple

import anthropic

from app import config as app_config
from app.models import (
    SessionState, ClassificationResult, NBAResult,
    Segment, Intent, Sentiment, NBAState
)
from app.engine.classifier import classify_behavior
from app.engine.nba_engine import determine_nba

# --- Debounce Tracking ---
_last_call_times: Dict[str, float] = {}

CLASSIFICATION_SYSTEM_PROMPT = """You are the AI classification engine for a Customer Engagement Center. Analyze the customer's behavioral signals and return a JSON classification.

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
}"""


def build_session_context(session: SessionState, customer_data: Optional[Dict[str, Any]]) -> str:
    """Builds a human-readable text summary of the session state for the LLM prompt."""
    lines = []

    # Page visit sequence
    page_views = [e.page for e in session.events if e.type == "page_view"]
    lines.append("== Page Visit Sequence ==")
    if page_views:
        for i, page in enumerate(page_views, 1):
            lines.append(f"  {i}. {page}")
    else:
        lines.append("  (no pages visited yet)")

    # Page visit counts
    lines.append("\n== Page Visit Counts ==")
    if session.page_visits:
        for page, count in session.page_visits.items():
            lines.append(f"  {page}: {count} visit(s)")
    else:
        lines.append("  (none)")

    # Dwell times
    lines.append("\n== Accumulated Dwell Times ==")
    if session.accumulated_dwell:
        for page, seconds in session.accumulated_dwell.items():
            lines.append(f"  {page}: {seconds:.1f}s")
    else:
        lines.append("  (none)")

    # Raw intent points
    lines.append("\n== Intent Signal Points ==")
    for intent, points in session.raw_intent_points.items():
        if points > 0:
            lines.append(f"  {intent.value}: {points:.1f}")

    # Sentiment signals
    lines.append("\n== Sentiment Signals ==")
    for sentiment, weight in session.sentiment_signals.items():
        if weight > 0:
            lines.append(f"  {sentiment.value}: {weight:.1f}")

    # Event stats
    total_events = len(session.events)
    rage_clicks = sum(1 for e in session.events if e.type == "rage_click")
    lines.append(f"\n== Session Stats ==")
    lines.append(f"  Total events: {total_events}")
    lines.append(f"  Rage clicks: {rage_clicks}")

    # Customer data (if logged in)
    if customer_data:
        profile = customer_data.get("profile", {})
        customer = profile.get("customer")
        history = customer_data.get("history", {})

        if customer:
            lines.append(f"\n== Customer Profile ==")
            lines.append(f"  Name: {customer.name}")
            lines.append(f"  Tier: {customer.tier}")
            lines.append(f"  Lifetime Value: ${customer.lifetime_value:,.2f}")

        cases = history.get("cases", [])
        if cases:
            lines.append(f"\n== Open Support Cases ==")
            for case in cases:
                lines.append(f"  - {case.id} | {case.status} | {case.subject}")

        sessions = history.get("sessions", [])
        if sessions:
            lines.append(f"\n== Historical Sessions (recent) ==")
            for s in sessions[-5:]:
                lines.append(f"  - Intent: {s.primary_intent.value}, Sentiment: {s.sentiment.value}, Outcome: {s.outcome}")
    else:
        lines.append("\n== Customer Profile ==")
        lines.append("  Anonymous visitor (not logged in)")

    return "\n".join(lines)


def llm_classify_behavior(session: SessionState, customer_data: Optional[Dict[str, Any]]) -> Tuple[ClassificationResult, NBAResult]:
    """Calls Claude API for classification, parses JSON, validates enums, returns results."""
    client = anthropic.Anthropic(api_key=app_config.ANTHROPIC_API_KEY, timeout=app_config.LLM_TIMEOUT)

    context = build_session_context(session, customer_data)

    message = client.messages.create(
        model=app_config.LLM_MODEL,
        max_tokens=app_config.LLM_MAX_TOKENS,
        system=CLASSIFICATION_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Analyze this customer session and classify:\n\n{context}"}
        ]
    )

    # Extract text from response
    raw_text = message.content[0].text.strip()

    # Parse JSON (handle markdown code blocks if present)
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    data = json.loads(raw_text)

    # Validate enums
    segment = Segment(data["segment"])
    primary_intent = Intent(data["primary_intent"])
    sentiment = Sentiment(data["sentiment"])
    nba_state = NBAState(data["nba_state"])

    # Validate intent_scores
    intent_scores = {}
    for key, value in data["intent_scores"].items():
        intent_scores[Intent(key)] = float(value)

    # Validate insights
    insights = data["insights"]
    assert insights.get("segment") and len(insights["segment"]) > 0, "Missing segment insight"
    assert insights.get("intent") and len(insights["intent"]) > 0, "Missing intent insight"
    assert insights.get("sentiment") and len(insights["sentiment"]) > 0, "Missing sentiment insight"

    classification = ClassificationResult(
        segment=segment,
        primary_intent=primary_intent,
        intent_scores=intent_scores,
        sentiment=sentiment,
        insights=insights
    )

    nba = NBAResult(
        state=nba_state,
        action_text=data["nba_action_text"],
        should_trigger_chat=bool(data["should_trigger_chat"])
    )

    return classification, nba


def safe_llm_classify(session: SessionState, customer_data: Optional[Dict[str, Any]]) -> Tuple[ClassificationResult, NBAResult]:
    """Wraps llm_classify_behavior with try/except, falls back to Phase 1 on any failure."""
    try:
        return llm_classify_behavior(session, customer_data)
    except Exception as e:
        print(f"[WARNING] LLM fallback: using Phase 1 rules (reason: {e})")
        classification = classify_behavior(session, customer_data)
        nba = determine_nba(classification)
        return classification, nba


def should_call_llm(session_id: str, session: Optional[SessionState] = None) -> bool:
    """Debounce check: returns True if >2 seconds since last call or rage_click detected."""
    now = time.time()
    last_time = _last_call_times.get(session_id, 0)

    # Always call if rage_click detected since last call
    if session:
        for event in reversed(session.events):
            if event.type == "rage_click" and event.timestamp > last_time:
                _last_call_times[session_id] = now
                return True

    # Debounce: only call if >2 seconds since last
    if (now - last_time) > 2.0:
        _last_call_times[session_id] = now
        return True

    return False
