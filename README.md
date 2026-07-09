# Virtual Steering Wheel using Hand Tracking

Professional, modular real-time computer vision starter project for building a webcam-based virtual steering wheel controller.

## Features

- Python 3.12+ architecture
- OpenCV webcam capture
- MediaPipe hand tracking (up to 2 hands)
- Landmark and connection rendering
- Real-time FPS overlay
- ESC key exit
- Graceful camera error handling
- Clean, extensible module boundaries for future steering logic

## Project Structure

```text
OpenCvAraba/
├── requirements.txt
├── README.md
└── src/
    ├── main.py
    ├── camera.py
    ├── hand_tracker.py
    ├── config.py
    └── utils.py
```

## Installation

```bash
python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

## Run

```bash
python src/main.py
```

## Design Notes

- `camera.py`: webcam lifecycle and read abstraction
- `hand_tracker.py`: MediaPipe detection + drawing logic
- `utils.py`: FPS calculation and drawing helpers
- `config.py`: immutable typed configuration objects
- `main.py`: orchestration layer (application flow)

Steering angle estimation and controller output are intentionally excluded at this stage to keep architecture-focused groundwork clean.
