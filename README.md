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
