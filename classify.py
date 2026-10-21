import time
import numpy as np
from PIL import Image
from ai_edge_litert.interpreter import Interpreter

model = Interpreter(
    model_path="models/mobilenet_v1.tflite",
    num_threads=2
)
model.allocate_tensors()

inp = model.get_input_details()[0]
out = model.get_output_details()[0]

image = Image.open("/home/drpeker/test.jpg")
image = image.convert("RGB").resize((224, 224))

data = np.asarray(image, dtype=inp["dtype"])
data = np.expand_dims(data, axis=0)

model.set_tensor(inp["index"], data)

start = time.perf_counter()
model.invoke()
elapsed = time.perf_counter() - start

scores = model.get_tensor(out["index"])[0]

if out["quantization"][0] > 0:
    scale, zero_point = out["quantization"]
    scores = (scores.astype(np.float32) - zero_point) * scale

top5 = np.argsort(scores)[-5:][::-1]

print("\nNeuroEye - İlk AI Analizi")
print("-------------------------")
for idx in top5:
    print(f"Class {idx}: {scores[idx]:.4f}")

print(f"\nInference süresi: {elapsed:.3f} saniye")
