import time
from datetime import datetime

from neurosupervisor import read_detections, analyze

TARGET = "person"
APPEAR_FRAMES = 3
DISAPPEAR_FRAMES = 3
MIN_CONFIDENCE = 0.50
INTERVAL = 0.5


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
                return "OBJECT_APPEARED"
        else:
            self.missing_count += 1
            self.seen_count = 0

            if self.present and self.missing_count >= DISAPPEAR_FRAMES:
                self.present = False
                return "OBJECT_DISAPPEARED"

        return None


def main():
    detector = EventDetector()

    print("NeuroEye Event Detector v0.2")
    print("Target:", TARGET)
    print("Appear confirmation:", APPEAR_FRAMES)
    print("Disappear confirmation:", DISAPPEAR_FRAMES)
    print("Minimum confidence:", MIN_CONFIDENCE)
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
                    timestamp = datetime.now().isoformat(
                        timespec="seconds"
                    )
                    print(
                        f"[{timestamp}] {event}: {TARGET}",
                        flush=True
                    )

            except Exception as exc:
                print("Detection error:", exc, flush=True)

            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print("\nEvent Detector stopped")


if __name__ == "__main__":
    main()
