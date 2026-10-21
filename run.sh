#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

case "${1:-live}" in
    live)
        exec .venv/bin/python neuroeye_live_STABLE.py
        ;;
    snapshot)
        exec .venv/bin/python neuroeye.py
        ;;
    classify)
        exec .venv/bin/python classify.py
        ;;
    detect)
        exec .venv/bin/python detect.py
        ;;
    *)
        echo "Kullanim: ./run.sh [live|snapshot|classify|detect]"
        exit 1
        ;;
esac
