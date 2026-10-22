import time
from datetime import datetime

from event_detector import (
    EventDetector,
    INTERVAL,
    read_detections,
    analyze,
)


class BehaviorManager:
    def __init__(self):
        self.mode = "AWARE"
        self.state = "BOOT"
        self.detector = EventDetector()

    def transition(self, new_state, reason):
        if self.state == new_state:
            return

        old_state = self.state
        self.state = new_state

        timestamp = datetime.now().strftime("%H:%M:%S")
        print(
            f"[{timestamp}] {old_state} -> "
            f"{new_state} | {reason}",
            flush=True
        )

    def handle_event(self, event):
        event_type = event["type"]
        target = event["target"]

        if event_type == "OBJECT_APPEARED":
            if self.state == "IDLE":
                self.transition(
                    "OBSERVING",
                    f"{target} appeared"
                )

        elif event_type == "OBJECT_DISAPPEARED":
            if self.state == "OBSERVING":
                self.transition(
                    "IDLE",
                    f"{target} disappeared"
                )

    def run(self):
        print("NeuroEye Behavior Manager v0.1")
        print("Autonomy mode:", self.mode)
        print("Press Ctrl+C to stop", flush=True)

        self.transition("IDLE", "System ready")

        try:
            while True:
                try:
                    raw = read_detections()

                    if raw is None:
                        raise RuntimeError(
                            "Detection data unavailable"
                        )

                    detections = analyze(raw)
                    event = self.detector.update(detections)

                    if event:
                        print(
                            f"EVENT: {event['type']} "
                            f"({event['target']})",
                            flush=True
                        )
                        self.handle_event(event)

                except Exception as exc:
                    print(
                        "Detection error:", exc,
                        flush=True
                    )

                time.sleep(INTERVAL)

        except KeyboardInterrupt:
            print("\nBehavior Manager stopped")


if __name__ == "__main__":
    BehaviorManager().run()
