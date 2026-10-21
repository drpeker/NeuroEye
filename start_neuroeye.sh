#!/bin/bash
cd /home/drpeker/neuroeye || exit 1

PY="$PWD/.venv/bin/python"

if ! pgrep -f '[p]ython neuroeye_live_STABLE.py' >/dev/null; then
    echo "NeuroEye baslatiliyor..."
    nohup "$PY" neuroeye_live_STABLE.py > /tmp/neuroeye.log 2>&1 &
fi

echo "NeuroEye sunucusu bekleniyor..."
READY=0
for i in $(seq 1 30); do
    if curl -fsS --max-time 1 http://127.0.0.1:8080/detections >/dev/null 2>&1; then
        READY=1
        break
    fi
    sleep 1
done

if [ "$READY" -ne 1 ]; then
    echo "HATA: NeuroEye sunucusu hazir degil."
    exit 1
fi

if ! pgrep -f '[p]ython neurosupervisor.py' >/dev/null; then
    echo "NeuroSupervisor baslatiliyor..."
    nohup "$PY" neurosupervisor.py > /tmp/neurosupervisor.log 2>&1 &
fi

echo "NeuroEye ve NeuroSupervisor hazir."
echo "Groq AI Planner aciliyor..."
exec "$PY" groq_planner.py
