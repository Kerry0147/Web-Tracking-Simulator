from app.models import ClassificationResult, NBAResult, NBAState, Sentiment, Segment, Intent

def determine_nba(classification: ClassificationResult) -> NBAResult:
    """
    Determines Next Best Action based on PRD 3.2 A Logic Matrix.
    """
    state = NBAState.PASSIVE
    action_text = "<Hard Code> Monitor behavior for signals."
    should_trigger_chat = False
    
    # Logic extracted from PRD 3.2 A
    
    # 1. CRITICAL Check
    # Rule: Sentiment = FRUSTRATED OR (Segment = AT_RISK AND Intent = TROUBLESHOOTING > 50%)
    is_frustrated = classification.sentiment == Sentiment.FRUSTRATED
    is_risk_troubleshooting = (
        classification.segment == Segment.AT_RISK and 
        classification.primary_intent == Intent.TROUBLESHOOTING and 
        classification.intent_scores.get(Intent.TROUBLESHOOTING, 0) > 50
    )
    
    if is_frustrated or is_risk_troubleshooting:
        state = NBAState.CRITICAL
        action_text = "<Hard Code> Proactive Outreach Recommended. Customer is struggling with a recurring technical issue."
        should_trigger_chat = True
        
    # 2. OPPORTUNITY Check
    # Rule: Intent = TROUBLESHOOTING > 60% AND Sentiment != FRUSTRATED
    elif (classification.primary_intent == Intent.TROUBLESHOOTING and 
          classification.intent_scores.get(Intent.TROUBLESHOOTING, 0) > 60 and 
          not is_frustrated):
        state = NBAState.OPPORTUNITY
        action_text = "<Hard Code> Suggest Self-Service Resources. Offer specific KB articles for monitor flickering."
        
    # 3. PASSIVE (Default)
    else:
        state = NBAState.PASSIVE
        if classification.primary_intent == Intent.PURCHASE_SIGNAL:
             action_text = "<Hard Code> Monitor for conversion. Customer exploring gaming laptops."
        else:
             action_text = "<Hard Code> Monitor behavior. No intervention required."

    return NBAResult(
        state=state,
        action_text=action_text,
        should_trigger_chat=should_trigger_chat
    )