# NeuroEye

Computer vision project for Raspberry Pi Zero 2 W.

## Hardware

- Raspberry Pi Zero 2 W
- OV5647 CSI camera

## System

- Debian 13 Trixie ARM64
- Python 3.13.5
- Picamera2
- LiteRT 2.3.0
- SSD MobileNet V2

## Installation

Clone the repository and run:

    ./install.sh

## Starting NeuroEye

Connect to Raspberry Pi via SSH.

    cd /home/drpeker/neuroeye
    ./run.sh live

This starts the camera, continuous object detection,
and the HTTP server on port 8080.

Open in a browser:

    http://neuroeye.local:8080

Other modes:

    ./run.sh snapshot
    ./run.sh classify
    ./run.sh detect

## HTTP endpoints

- / : Web interface
- /stream : MJPEG video
- /detections : JSON detections

## Recovery

1. Install Debian 13 ARM64.
2. Enable the OV5647 camera.
3. Clone the repository.
4. Run ./install.sh.
5. Start using ./run.sh live.

## System inventory

Original package versions and hardware information
are stored in docs/system-inventory/.

## Development

The original working source code and AI models
are preserved in this repository.

Future NeuroSupervisor development should use
a separate Git branch.
## NeuroSupervisor and Groq AI Planner

NeuroEye now includes an experimental AI task-planning system.

### Components

- **NeuroEye:** OV5647 camera, SSD MobileNet V2 object detection, and HTTP server on port 8080.
- **NeuroSupervisor (`neurosupervisor.py`):** Reads live detection data from NeuroEye.
- **Task Protocol (`task_protocol.py`):** Validates structured robot tasks and provides simulation output.
- **Groq Planner (`groq_planner.py`):** Converts Turkish or English natural-language commands into structured JSON tasks using the Groq API.

Current Groq model: `qwen/qwen3.8-27b`.

### Unified startup

From the Raspberry Pi terminal, run:

```bash
neuro-eye
```

The launcher (`start_neuroeye.sh`) starts NeuroEye if needed, waits for the detection endpoint, starts NeuroSupervisor if needed, and opens the interactive Groq Planner.

Already-running components are not restarted.

Example commands:

```text
Komut > beni takip et
Komut > dur
Komut > mavi kupayı bul ve yanına git
```

Type `exit` to leave the interactive planner. NeuroEye and NeuroSupervisor remain running.

No automatic startup at Raspberry Pi boot is configured.

### API configuration

Create a local `.env` file containing:

```text
GROQ_API_KEY=your_api_key_here
```

Keep this file private. It is excluded from Git tracking.

### Current limitations

- Motor control is disabled; robot motion is simulation-only.
- Groq Planner and the live NeuroSupervisor process are not yet integrated into a single task execution loop.
- Color verification and person identity recognition are not yet implemented.
- Multi-step plans are interpreted but not yet executed autonomously.

### Version history

- `v1.0-baseline` — Working NeuroEye camera and detection system.
- `v0.1-ai-planner` — NeuroSupervisor, task protocol, and tested Groq AI task planning.

Active development branch: `feature/neurosupervisor`.

### Next milestone

NeuroSupervisor v0.2 will integrate AI-generated tasks with live NeuroEye detections through a controlled task state machine, initially without physical motor control.
