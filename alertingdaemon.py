import asyncio
import logging
from collections import deque
from datetime import datetime, timedelta

class AnomalyDetector:
    def __init__(self, threshold=3, window_sec=60):
        self.threshold = threshold
        self.window_sec = window_sec
        self.events = deque()

    def record_event(self, event_type):
        now = datetime.utcnow()
        self.events.append((now, event_type))
        self.clean_old_events(now)

    def clean_old_events(self, now):
        while self.events and (now - self.events[0][0]).total_seconds() > self.window_sec:
            self.events.popleft()

    def detect_anomaly(self):
        counts = {}
        for _, etype in self.events:
            counts[etype] = counts.get(etype, 0) + 1

        for etype, count in counts.items():
            if count > self.threshold:
                logging.warning(f"Anomaly detected: {etype} count={count} in last {self.window_sec}s")
                return etype, count
        return None, 0

async def alerting_loop(detector):
    while True:
        anomaly = detector.detect_anomaly()
        if anomaly[0]:
            print(f"🚨 ALERT: {anomaly[0]} anomaly with count {anomaly[1]}")
            # Integrate here: send message to Discord/Slack/email webhook
        await asyncio.sleep(5)

async def main_event_simulator(detector):
    # Simulate random events
    import random
    event_types = ["burn_proposal", "vault_deposit", "vault_withdraw", "dao_vote"]

    while True:
        event = random.choice(event_types)
        detector.record_event(event)
        await asyncio.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    detector = AnomalyDetector(threshold=5, window_sec=30)
    loop = asyncio.get_event_loop()
    loop.create_task(alerting_loop(detector))
    loop.create_task(main_event_simulator(detector))
    loop.run_forever()
