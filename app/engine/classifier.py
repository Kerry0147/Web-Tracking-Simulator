from typing import Dict, Any, Optional
from datetime import datetime
from app.models import (
    SessionState, ClassificationResult, Segment, Intent, Sentiment, 
    Customer, Case, HistoricalSession
)
from app.engine.behavior_tracker import tracker

def classify_behavior(session: SessionState, customer_data: Optional[Dict[str, Any]] = None) -> ClassificationResult:
    """
    Applies PRD rules to determine Segment, Intent, and Sentiment.
    """
    # 1. Calculate Intent & Sentiment using BehaviorTracker
    normalized_intents = tracker.get_normalized_intents(session)
    primary_intent = max(normalized_intents, key=normalized_intents.get)
    current_sentiment = tracker.get_current_sentiment(session)
    
    # 2. Determine Segment (PRD 3.2 C Priority Rules)
    segment = Segment.NEW_VISITOR # Default
    segment_insight = "<Hard Code> Visitor is anonymous. No history available."
    
    if customer_data:
        customer: Customer = customer_data.get("profile", {}).get("customer")
        history = customer_data.get("history", {})
        cases: list[Case] = history.get("cases", [])
        sessions: list[HistoricalSession] = history.get("sessions", [])
        
        # Rule 1: AT_RISK (Open Unresolved Case OR Recurrent Issue)
        has_open_case = any(c.status == "Open" for c in cases)
        
        # Recurrence check: Count how many times primary intent appears in recent sessions
        # (Current session counts as 1)
        intent_count = 1 
        for s in sessions:
            if s.primary_intent == primary_intent:
                intent_count += 1
                
        is_recurrent = intent_count >= 3
        
        if has_open_case or is_recurrent:
            segment = Segment.AT_RISK
            if has_open_case:
                segment_insight = "<Hard Code> Customer has an open unresolved case (CASE-2026-0891). Risk of churn is elevated."
            else:
                segment_insight = "<Hard Code> Customer has visited for the same issue 3 times in 30 days. Elevated attention recommended."
                
        # Rule 2: VIP (Gold/Platinum AND LTV > 2000)
        elif customer and customer.tier in ["Gold", "Platinum"] and customer.lifetime_value > 2000:
            segment = Segment.VIP
            segment_insight = f"<Hard Code> High-value {customer.tier} customer with LTV ${customer.lifetime_value:,.2f}."
            
        # Rule 3: DORMANT (Last visit > 90 days) - *Simplified logic for PoC*
        # In a real app we'd check dates. For this PoC, we'll skip complex date math 
        # unless specifically needed, defaulting to Returning if history exists.
        
        # Rule 4: RETURNING
        elif len(sessions) > 0:
            segment = Segment.RETURNING
            segment_insight = "<Hard Code> Returning customer with previous session history."
            
    # 3. Generate Insights (Hardcoded per PRD Phase 1)
    
    # Intent Insight
    intent_score = normalized_intents.get(primary_intent, 0)
    intent_insight = f"<Hard Code> Primary intent is {primary_intent.value} ({intent_score}%)."
    
    if primary_intent == Intent.TROUBLESHOOTING and intent_score > 70:
        intent_insight = "<Hard Code> Customer is focused on troubleshooting content. Repeated visits to monitor-related KB articles suggest an unresolved technical issue."
    elif primary_intent == Intent.WARRANTY_INQUIRY:
        intent_insight = "<Hard Code> Customer is actively checking warranty status, likely assessing repair options."
    elif primary_intent == Intent.PURCHASE_SIGNAL:
        intent_insight = "<Hard Code> Customer showing strong purchase signals on high-value gaming products."

    # Sentiment Insight
    sentiment_insight = "<Hard Code> Behavior indicates normal browsing patterns."
    
    if current_sentiment == Sentiment.FRUSTRATED:
        sentiment_insight = "<Hard Code> Behavioral signals indicate difficulty — rapid page switching and repeated page revisits suggest the customer is not finding what they need."
    elif current_sentiment == Sentiment.CONFUSED:
        sentiment_insight = "<Hard Code> Navigation loops detected. Customer is revisiting the same pages multiple times."
    elif current_sentiment == Sentiment.POSITIVE:
        sentiment_insight = "<Hard Code> Steady dwell times and linear navigation indicate good engagement."

    return ClassificationResult(
        segment=segment,
        primary_intent=primary_intent,
        intent_scores=normalized_intents,
        sentiment=current_sentiment,
        insights={
            "segment": segment_insight,
            "intent": intent_insight,
            "sentiment": sentiment_insight
        }
    )