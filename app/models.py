from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

# --- Enums (Constants) ---

class Segment(str, Enum):
    NEW_VISITOR = "NEW_VISITOR"
    RETURNING = "RETURNING"
    VIP = "VIP"
    AT_RISK = "AT_RISK"
    DORMANT = "DORMANT"

class Intent(str, Enum):
    GENERAL_BROWSING = "GENERAL_BROWSING"
    TROUBLESHOOTING = "TROUBLESHOOTING"
    WARRANTY_INQUIRY = "WARRANTY_INQUIRY"
    PURCHASE_SIGNAL = "PURCHASE_SIGNAL"
    CASE_FOLLOW_UP = "CASE_FOLLOW_UP"

class Sentiment(str, Enum):
    NEUTRAL = "NEUTRAL"
    POSITIVE = "POSITIVE"
    CONFUSED = "CONFUSED"
    FRUSTRATED = "FRUSTRATED"
    CAUTIOUS = "CAUTIOUS"  # Matches mock_data.json

class NBAState(str, Enum):
    PASSIVE = "PASSIVE"
    OPPORTUNITY = "OPPORTUNITY"
    CRITICAL = "CRITICAL"

# --- Live Session Models (Layer 4) ---

class BehaviorEvent(BaseModel):
    type: str  # "page_view", "click", "scroll", "rage_click"
    page: str
    timestamp: float
    element: Optional[str] = None
    dwell_time: Optional[float] = 0.0
    metadata: Optional[Dict[str, Any]] = None

class SessionState(BaseModel):
    session_id: str
    customer_id: Optional[str] = None
    start_time: float
    events: List[BehaviorEvent] = []
    
    # Tracking Accumulators
    page_visits: Dict[str, int] = {}
    accumulated_dwell: Dict[str, float] = {}
    
    # Scoring Buckets
    raw_intent_points: Dict[Intent, float] = {i: 0.0 for i in Intent}
    sentiment_signals: Dict[Sentiment, float] = {s: 0.0 for s in Sentiment}

    # Chat Trigger Flag
    chat_triggered: bool = False 

class ClassificationResult(BaseModel):
    segment: Segment
    primary_intent: Intent
    intent_scores: Dict[Intent, float]
    sentiment: Sentiment
    insights: Dict[str, str]

class NBAResult(BaseModel):
    state: NBAState
    action_text: str
    should_trigger_chat: bool

# --- Static Data Models (Matches mock_data.json) ---

class Device(BaseModel):
    id: str
    customer_id: str
    product_name: str
    serial_number: str
    purchase_date: str
    purchase_price: Optional[float] = None
    image_url: str
    # 'warranty' is injected at runtime in main.py, not in raw JSON
    warranty: Optional[Any] = None 

class Warranty(BaseModel):
    id: str
    device_id: str
    customer_id: str
    status: str
    start_date: str
    end_date: str # JSON uses 'end_date', not 'expiration_date'
    type: str

class Customer(BaseModel):
    id: str
    name: str
    email: str
    tier: str
    location: str
    customer_since: str # JSON uses 'customer_since', not 'join_date'
    lifetime_value: float
    avatar_url: Optional[str] = None

class HistoricalSession(BaseModel):
    session_id: str # JSON uses 'session_id', not 'id'
    customer_id: str
    date: str
    duration_minutes: int # JSON uses 'duration_minutes', not 'seconds'
    pages_visited_count: Optional[int] = None
    primary_intent: Intent
    sentiment: Sentiment
    outcome: str
    key_insight: Optional[str] = None
    page_flow: Optional[List[str]] = None

class CaseInteraction(BaseModel):
    date: str
    channel: str
    summary: str

class Case(BaseModel):
    id: str
    customer_id: str
    device_id: str
    subject: str # JSON uses 'subject', not 'title'
    status: str
    creation_date: str # JSON uses 'creation_date'
    last_update_date: Optional[str] = None
    resolution: Optional[str] = None
    linked_case_id: Optional[str] = None
    interaction_log: Optional[List[CaseInteraction]] = None
    
    # Injected at runtime
    linked_case: Optional[Any] = None
    device_name: Optional[str] = None