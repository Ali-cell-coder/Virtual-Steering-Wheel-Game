"""Launcher for the Virtual Steering Wheel project."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
STEERING_SCRIPT = PROJECT_ROOT / "src" / "main.py"
GAME_SCRIPT = PROJECT_ROOT / "game" / "main.py"
POLL_INTERVAL_SEC = 0.2
TERMINATE_TIMEOUT_SEC = 5.0


def _start_process(name: str, script_path: Path) -> subprocess.Popen[bytes]:
    print(f"Starting {name}...")
    return subprocess.Popen([sys.executable, str(script_path)])


def _terminate_process(name: str, process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return

    print(f"Stopping {name}...")
    process.terminate()
    try:
        process.wait(timeout=TERMINATE_TIMEOUT_SEC)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def main() -> int:
    processes: list[tuple[str, subprocess.Popen[bytes]]] = []
    exit_code = 0

    try:
        steering_process = _start_process("Steering System", STEERING_SCRIPT)
        game_process = _start_process("Driving Game", GAME_SCRIPT)
        processes = [
            ("Steering System", steering_process),
            ("Driving Game", game_process),
        ]

        while True:
            for name, process in processes:
                return_code = process.poll()
                if return_code is not None:
                    print(f"{name} exited with code {return_code}.")
                    exit_code = return_code
                    raise RuntimeError(f"{name} stopped unexpectedly.")

            time.sleep(POLL_INTERVAL_SEC)

    except KeyboardInterrupt:
        print("\nShutting down...")
        exit_code = 0
    except RuntimeError:
        print("Shutting down...")
    finally:
        for name, process in processes:
            _terminate_process(name, process)

        print("Shutdown complete.")
        return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
