import json
import time
from urllib.request import urlopen
from urllib.error import URLError

URL = "http://127.0.0.1:8080/detections"
WIDTH = 640
HEIGHT = 480
INTERVAL = 0.5
MIN_CONFIDENCE = 0.40


def read_detections():
    with urlopen(URL, timeout=1.0) as response:
        return json.load(response)


def analyze(detections):
    results = []

    for obj in detections:
        confidence = float(obj["confidence"])
        if confidence < MIN_CONFIDENCE:
            continue

        x1, y1, x2, y2 = obj["box"]
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

        relative_x = (cx / WIDTH - 0.5) * 2
        relative_y = (cy / HEIGHT - 0.5) * 2

        if relative_x < -0.25:
            direction = "LEFT"
        elif relative_x > 0.25:
            direction = "RIGHT"
        else:
            direction = "CENTER"

        area_ratio = ((x2 - x1) * (y2 - y1)) / (WIDTH * HEIGHT)

        results.append({
            "class": obj["class"],
            "confidence": confidence,
            "direction": direction,
            "x": round(relative_x, 3),
            "y": round(relative_y, 3),
            "area": round(area_ratio, 3),
        })

    return results


def main():
    print("NeuroSupervisor v0.1 started")
    print("Source:", URL)
    print("Press Ctrl+C to stop")

    previous = None

    try:
        while True:
            try:
                detections = read_detections()
                results = analyze(detections)

                signature = json.dumps(results, sort_keys=True)

                if signature != previous:
                    print(json.dumps(results, indent=2))
                    previous = signature

            except (URLError, TimeoutError, OSError) as exc:
                print("NeuroEye unavailable:", exc)
                previous = None

            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print("\nNeuroSupervisor stopped")


if __name__ == "__main__":
    main()
