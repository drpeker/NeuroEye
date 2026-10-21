import json
import subprocess
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from ai_edge_litert.interpreter import Interpreter

BASE = Path.home() / "neuroeye"
MODEL = BASE / "models/ssd_mobilenet_v2.tflite"
LABELS = BASE / "models/coco_labels.txt"
PHOTO = BASE / "capture.jpg"
RESULT = BASE / "detected.jpg"
JSON_FILE = BASE / "detections.json"

THRESHOLD = 0.35

def capture():
    print("Kameradan yeni görüntü alınıyor...")
    subprocess.run([
        "rpicam-still",
        "-n", "-t", "500",
        "--width", "640",
        "--height", "480",
        "-o", str(PHOTO)
    ], check=True, stdout=subprocess.DEVNULL)
    print("Fotoğraf:", PHOTO)

def load_labels():
    labels = {}
    with open(LABELS) as f:
        for line in f:
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2 and parts[0].isdigit():
                labels[int(parts[0])] = parts[1]
    return labels

def main():
    capture()

    labels = load_labels()

    interpreter = Interpreter(
        model_path=str(MODEL),
        num_threads=2
    )
    interpreter.allocate_tensors()

    inp = interpreter.get_input_details()[0]
    outs = interpreter.get_output_details()

    image = Image.open(PHOTO).convert("RGB")
    width, height = image.size

    input_h = int(inp["shape"][1])
    input_w = int(inp["shape"][2])

    resized = image.resize((input_w, input_h))
    data = np.asarray(resized, dtype=inp["dtype"])

    if np.issubdtype(inp["dtype"], np.floating):
        data = (data.astype(np.float32) - 127.5) / 127.5

    data = np.expand_dims(data, axis=0)
    interpreter.set_tensor(inp["index"], data)

    print("AI analizi yapılıyor...")
    start = time.perf_counter()
    interpreter.invoke()
    elapsed = time.perf_counter() - start

    boxes = interpreter.get_tensor(outs[0]["index"])[0]
    classes = interpreter.get_tensor(outs[1]["index"])[0]
    scores = interpreter.get_tensor(outs[2]["index"])[0]
    count = int(interpreter.get_tensor(outs[3]["index"])[0])

    draw = ImageDraw.Draw(image)
    detections = []

    for i in range(min(count, len(scores))):
        score = float(scores[i])
        if score < THRESHOLD:
            continue

        cls = int(classes[i])
        name = labels.get(cls, f"class_{cls}")

        ymin, xmin, ymax, xmax = boxes[i]
        x1 = max(0, min(width, int(xmin * width)))
        y1 = max(0, min(height, int(ymin * height)))
        x2 = max(0, min(width, int(xmax * width)))
        y2 = max(0, min(height, int(ymax * height)))

        if x2 <= x1 or y2 <= y1:
            continue

        draw.rectangle((x1, y1, x2, y2),
                       outline="red", width=3)
        draw.text((x1, max(0, y1 - 14)),
                  f"{name} {score:.0%}", fill="yellow")

        detections.append({
            "class": name,
            "confidence": round(score, 4),
            "box": [x1, y1, x2, y2]
        })

    image.save(RESULT)

    result = {
        "device": "neuroeye",
        "model": "SSD MobileNet V2",
        "inference_ms": round(elapsed * 1000, 1),
        "detections": detections
    }

    JSON_FILE.write_text(json.dumps(result, indent=2))

    print("\n--- NeuroEye Vision AI ---")
    print(json.dumps(result, indent=2))
    print("\nFotoğraf:", RESULT)
    print("JSON:", JSON_FILE)

if __name__ == "__main__":
    main()
