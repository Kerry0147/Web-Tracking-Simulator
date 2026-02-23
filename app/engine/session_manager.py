import time
import uuid
from typing import Dict, Optional
from app.models import SessionState, BehaviorEvent, Intent, Sentiment

class SessionManager:
    def __init__(self):
        # In-memory storage: session_id -> SessionState object
        self._sessions: Dict[str, SessionState] = {}

    def get_or_create(self, session_id: Optional[str] = None) -> SessionState:
        """Retrieves an existing session or creates a new one."""
        if session_id and session_id in self._sessions:
            return self._sessions[session_id]
        
        # Create new session
        new_id = session_id or str(uuid.uuid4())
        new_session = SessionState(
            session_id=new_id,
            start_time=time.time(),
            events=[],
            page_visits={},
            accumulated_dwell={},
            raw_intent_points={i: 0.0 for i in Intent},
            sentiment_signals={s: 0 for s in Sentiment}
        )
        self._sessions[new_id] = new_session
        print(f"✨ New Session Created: {new_id}")
        return new_session

    def get_session(self, session_id: str) -> Optional[SessionState]:
        return self._sessions.get(session_id)

    def update_customer(self, session_id: str, customer_id: Optional[str]):
        """Links a session to a logged-in customer."""
        if session_id in self._sessions:
            self._sessions[session_id].customer_id = customer_id

    def remove_session(self, session_id: str):
        """Removes a session from memory entirely."""
        self._sessions.pop(session_id, None)

# Global instance
session_manager = SessionManager()