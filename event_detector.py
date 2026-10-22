import json
import time
from datetime import datetime, timezone

from neurosupervisor import read_detections, analyze

TARGET = "person"
APPEAR_FRAMES = 3
DISAPPEAR_FRAMES = 3
MIN_CONFIDENCE = 0.50
INTERVAL = 0.2


class EventDetector:
    def __init__(self):
        self.present = False
        self.seen_count = 0
        self.missing_count = 0

    def update(self, detections):
        matches = [
            obj for obj in detections
            if obj["class"] == TARGET
            and obj["confidence"] >= MIN_CONFIDENCE
        ]

        if matches:
            self.seen_count += 1
            self.missing_count = 0

            if not self.present and self.seen_count >= APPEAR_FRAMES:
                self.present = True
                event_type = "OBJECT_APPEARED"
            else:
                return None
        else:
            self.missing_count += 1
            self.seen_count = 0

            if self.present and self.missing_count >= DISAPPEAR_FRAMES:
                self.present = False
                event_type = "OBJECT_DISAPPEARED"
            else:
                return None

        return {
            "type": event_type,
            "source": "neuroeye",
            "target": TARGET,
            "timestamp": datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            ),
        }


def main():
    detector = EventDetector()

    print("NeuroEye Event Detector v0.3", flush=True)
    print("Target:", TARGET, flush=True)
    print("Mode: Structured JSON events", flush=True)
    print("Press Ctrl+C to stop", flush=True)

    try:
        while True:
            try:
                raw = read_detections()

                if raw is None:
                    raise RuntimeError("Detection data unavailable")

                detections = analyze(raw)
                event = detector.update(detections)

                if event:
                    print(
                        json.dumps(event, ensure_ascii=False),
                        flush=True
                    )

            except Exception as exc:
                print("Detection error:", exc, flush=True)

            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print("\nEvent Detector stopped")


if __name__ == "__main__":
    main()
