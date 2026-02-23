from typing import Dict, Any, Optional
from app.models import SessionState, ClassificationResult, NBAResult
from app.skills.read_skills import get_customer_profile, get_customer_history
from app.engine.classifier import classify_behavior
from app.engine.nba_engine import determine_nba
from app import config as app_config
from app.engine.llm_client import safe_llm_classify, should_call_llm

# Module-level cache for debounced calls
_last_result: Dict[str, tuple] = {}

class RoutingSkills:
    def execute_classification(self, session: SessionState, mock_data: Dict[str, Any]) -> tuple[ClassificationResult, NBAResult]:
        """
        Orchestrates full analysis:
        1. Loads customer context (if logged in)
        2. runs Classifier
        3. runs NBA Engine
        """
        customer_context = None

        # If user is logged in, fetch full profile & history
        if session.customer_id:
            profile = get_customer_profile(session.customer_id, mock_data)
            history = get_customer_history(session.customer_id, mock_data)

            if profile:
                customer_context = {
                    "profile": profile,
                    "history": history
                }

        if app_config.AI_MODE == "phase2" and should_call_llm(session.session_id, session):
            # Use LLM (with automatic fallback built into safe_llm_classify)
            classification, nba = safe_llm_classify(session, customer_context)
            _last_result[session.session_id] = (classification, nba)
        elif app_config.AI_MODE == "phase2" and session.session_id in _last_result:
            # Debounce: return cached result
            classification, nba = _last_result[session.session_id]
        else:
            # Phase 1 original logic (unchanged)
            classification = classify_behavior(session, customer_context)
            nba = determine_nba(classification)

        return classification, nba

# Global instance
router = RoutingSkills()
