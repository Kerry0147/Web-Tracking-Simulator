import time
from typing import Dict
from app.models import SessionState, BehaviorEvent, Intent, Sentiment

class BehaviorTracker:
    def process_event(self, session: SessionState, event_data: dict):
        """
        Ingests a raw event, updates session history, and recalculates scores.
        """
        event = BehaviorEvent(**event_data)

        # PREVENT DUPLICATE EVENTS (Debounce)
        if event.type == "page_view" and session.events:
            last_event = session.events[-1]
            if last_event.type == "page_view" and last_event.page == event.page:
                 if (event.timestamp - last_event.timestamp) < 0.5:
                     return 

        session.events.append(event)

        # 1. Update Page History & Dwell
        if event.type == "page_view":
            path = event.page
            session.page_visits[path] = session.page_visits.get(path, 0) + 1
            
            # Baseline points
            self._add_points(session, Intent.GENERAL_BROWSING, 3.0)
            
            # ✅ UPDATED: AGGRESSIVE SENTIMENT COOL DOWN
            # One normal click should fix a "Rage Click" immediately.
            # Was: -10 (Too slow). Now: -30 (Instant relief).
            if session.sentiment_signals[Sentiment.FRUSTRATED] > 0:
                session.sentiment_signals[Sentiment.FRUSTRATED] -= 30 
                if session.sentiment_signals[Sentiment.FRUSTRATED] < 0:
                    session.sentiment_signals[Sentiment.FRUSTRATED] = 0
                print(f"❄️ Sentiment Cooling Down... (Frustrated Score: {session.sentiment_signals[Sentiment.FRUSTRATED]})")

            if session.sentiment_signals[Sentiment.CONFUSED] > 0:
                session.sentiment_signals[Sentiment.CONFUSED] -= 15 # Faster confusion recovery too

            # Check for Revisit Pattern (Confusion)
            if session.page_visits[path] > 2:
                session.sentiment_signals[Sentiment.CONFUSED] += 100
                print(f"⚠️ Revisit #{session.page_visits[path]} on {path} (+100 Confused)")

        elif event.type == "page_leave":
            if event.dwell_time:
                session.accumulated_dwell[event.page] = session.accumulated_dwell.get(event.page, 0.0) + event.dwell_time
                self._score_dwell_time(session, event.page, event.dwell_time)

        # 2. Apply Intent Scoring
        self._apply_intent_rules(session, event)

        # 3. Apply Sentiment Scoring
        self._apply_sentiment_rules(session, event)

    def get_normalized_intents(self, session: SessionState) -> Dict[Intent, float]:
        raw = session.raw_intent_points
        total_points = sum(raw.values())
        if total_points == 0:
            return {i: (100.0 if i == Intent.GENERAL_BROWSING else 0.0) for i in Intent}
        return {k: round((v / total_points) * 100, 1) for k, v in raw.items()}

    def get_current_sentiment(self, session: SessionState) -> Sentiment:
        signals = session.sentiment_signals
        
        # 1. Frustration Override (Threshold logic)
        # Only trigger FRUSTRATED if score is significant (>20)
        if signals.get(Sentiment.FRUSTRATED, 0) > 20:
            return Sentiment.FRUSTRATED
        
        # 2. Find highest weighted signal
        max_weight = 0
        dominant = Sentiment.NEUTRAL
        
        # Debug Log
        scores_log = ", ".join([f"{k.value}={v}" for k,v in signals.items() if v > 0])
        if scores_log:
            print(f"📊 SCORE BATTLE: {scores_log}")

        for sentiment, weight in signals.items():
            if weight > max_weight:
                max_weight = weight
                dominant = sentiment
                
        return dominant

    # --- Internal Scoring Logic ---

    def _add_points(self, session: SessionState, intent: Intent, points: float):
        session.raw_intent_points[intent] += points

    def _apply_intent_rules(self, session: SessionState, event: BehaviorEvent):
        page = event.page
        if "/troubleshooting" in page:
            if event.type == "page_view":
                points = 20.0 if len(page.split("/")) > 3 else 15.0
                self._add_points(session, Intent.TROUBLESHOOTING, points)
        if "/warranty" in page:
            if event.type == "page_view":
                self._add_points(session, Intent.WARRANTY_INQUIRY, 25.0)
            elif event.type == "form_submit":
                self._add_points(session, Intent.WARRANTY_INQUIRY, 30.0)
        if "/case-status" in page:
            if event.type == "page_view":
                self._add_points(session, Intent.CASE_FOLLOW_UP, 25.0)
            elif event.type == "form_submit" or "click" in event.type:
                self._add_points(session, Intent.CASE_FOLLOW_UP, 30.0)
        if "/products" in page:
            if event.type == "page_view":
                points = 15.0 if len(page.split("/")) > 3 else 5.0
                self._add_points(session, Intent.PURCHASE_SIGNAL, points)
        if event.type == "click" and event.element == "buy-button":
             self._add_points(session, Intent.PURCHASE_SIGNAL, 50.0)

    def _score_dwell_time(self, session: SessionState, page: str, seconds: float):
        if "/troubleshooting" in page and seconds > 10:
            self._add_points(session, Intent.TROUBLESHOOTING, 10.0)
            session.sentiment_signals[Sentiment.POSITIVE] += 10 
        if "/products" in page and seconds > 30:
            self._add_points(session, Intent.PURCHASE_SIGNAL, 15.0)

    def _apply_sentiment_rules(self, session: SessionState, event: BehaviorEvent):
        if event.type == "rage_click":
            session.sentiment_signals[Sentiment.FRUSTRATED] += 40
            print("🤬 RAGE CLICK DETECTED!")

tracker = BehaviorTracker()