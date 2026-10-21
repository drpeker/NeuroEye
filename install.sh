#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "NeuroEye - Debian 13 ARM64 kurulumu"

sudo apt update

sudo apt install -y \
    python3 \
    python3-venv \
    python3-pip \
    python3-picamera2 \
    python3-numpy \
    python3-pil \
    rpicam-apps-lite \
    libcamera-tools

if [ ! -d .venv ]; then
    python3 -m venv --system-site-packages .venv
fi

.venv/bin/python -m pip install "ai-edge-litert==2.3.0"

echo "===== MODUL KONTROLU ====="
.venv/bin/python - <<'PY'
import numpy
from PIL import Image
from picamera2 import Picamera2
from ai_edge_litert.interpreter import Interpreter

print("NumPy:", numpy.__version__)
print("Picamera2: OK")
print("Pillow: OK")
print("LiteRT: OK")
PY

echo "NeuroEye kurulumu tamamlandi."
