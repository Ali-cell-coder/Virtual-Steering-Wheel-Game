#  Virtual Steering Wheel Game

A real-time computer vision driving game that lets you control a car using a **virtual steering wheel** detected from your hands with **OpenCV** and **MediaPipe**.

The project combines hand tracking and a 2D driving game to demonstrate real-time human-computer interaction.

---

# Features

-  Real-time hand tracking using MediaPipe
-  Webcam-based virtual steering wheel
-  2D driving game built with Pygame
-  Traffic vehicles with random spawning
-  Collision detection
-  Crash sound effects
-  Distance counter
-  High Score system
-  Countdown before gameplay
-  Restart after Game Over
-  Progressive game speed
-  Modular project architecture

---

# Technologies

- Python 3.12
- OpenCV
- MediaPipe
- Pygame
- NumPy

---

# Project Structure

```text
Virtual-Steering-Wheel-Game/
│
├── assets/
│
├── game/
│   ├── assets/
│   ├── data/
│   ├── main.py
│   ├── game_engine.py
│   ├── traffic.py
│   ├── traffic_car.py
│   ├── steering_controller.py
│   └── ...
│
├── src/
│   ├── main.py
│   ├── camera.py
│   ├── hand_tracker.py
│   ├── steering_socket_server.py
│   └── ...
│
├── requirements.txt
├── README.md
└── run.py
```

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/Ali-cell-coder/Virtual-Steering-Wheel-Game.git
cd Virtual-Steering-Wheel-Game
```

## 2. Create a virtual environment

```bash
py -3.12 -m venv .venv
```

## 3. Activate the virtual environment

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

---
# Running the Project

After completing the installation:

1. Double-click **start_project.bat**

The launcher will automatically:

- Activate the virtual environment
- Start the hand tracking application
- Start the driving game

No additional commands are required.

# Gameplay

1. Start **Hand Tracking**.
2. Start the **Driving Game**.
3. Allow camera access if Windows asks.
4. Place both hands in front of the webcam.
5. Wait for the countdown.
6. Turn the virtual steering wheel.
7. Avoid traffic vehicles.
8. Try to beat your High Score.

---

# Controls

| Action | Description |
|---------|-------------|
| Steering Wheel | Control the vehicle |
| ESC | Exit the game |
| Restart Button | Restart after Game Over |

---

# Screenshots

Add screenshots or GIFs here.

Example:

```
assets/screenshots/gameplay.png
```

---

# Future Improvements

- Multiple road themes
- More vehicle types
- Difficulty levels
- Lane changing AI
- Better visual effects
- Score leaderboard

## Quick Start

### First time setup

```bash
git clone https://github.com/Ali-cell-coder/Virtual-Steering-Wheel-Game.git
cd Virtual-Steering-Wheel-Game
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run

Double-click `start_project.bat`.

