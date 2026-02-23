# test_layer5.py
import json
from app.models import SessionState, Intent, Sentiment, BehaviorEvent, Segment, NBAState
from app.engine.behavior_tracker import tracker
from app.skills.routing_skills import router

# 1. Load Mock Data
with open('app/data/mock_data.json', 'r') as f:
    mock_data = json.load(f)

# 2. Setup Mock Session (Sarah Logged In)
session = SessionState(
    session_id="test-session-123",
    start_time=1234567890,
    customer_id="CUST-2024-0847" # Sarah Chen
)

# 3. Simulate Behavior: Frustrated Troubleshooting
# Add page views
for _ in range(3):
    tracker.process_event(session, {"type": "page_view", "page": "/troubleshooting/monitor", "timestamp": 0})
# Add rage click
tracker.process_event(session, {"type": "rage_click", "page": "/troubleshooting/monitor", "timestamp": 0, "element": "btn"})

# 4. Run Classification
classification, nba = router.execute_classification(session, mock_data)

# 5. Verify Results
print(f"Segment: {classification.segment}") 
# Expected: Segment.AT_RISK (Because she has an open case in mock_data)

print(f"Sentiment: {classification.sentiment}") 
# Expected: Sentiment.FRUSTRATED (Because of rage click)

print(f"NBA State: {nba.state}")
# Expected: NBAState.CRITICAL (Because Frustrated + At Risk)

print(f"Action: {nba.action_text}")
# Expected: <Hard Code> Proactive Outreach...

if classification.segment == Segment.AT_RISK and nba.state == NBAState.CRITICAL:
    print("\n✅ Layer 5 Verification PASSED")
else:
    print("\n❌ Layer 5 Verification FAILED")