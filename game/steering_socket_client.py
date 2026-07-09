"""TCP client for receiving normalized steering values from OpenCV."""

from __future__ import annotations

import socket
import threading
import time


class SteeringSocketClient:
    """Receives steering values from the OpenCV steering server."""

    def __init__(self, host: str = "127.0.0.1", port: int = 5555) -> None:
        self._host = host
        self._port = port
        self._value: float | None = None
        self._connected = False
        self._lock = threading.Lock()
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start the background receive loop."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the background receive loop."""
        self._running = False

    def is_connected(self) -> bool:
        """Return True when a live socket connection is active."""
        with self._lock:
            return self._connected

    def get_value(self) -> float | None:
        """Return the latest received steering value when connected."""
        with self._lock:
            if not self._connected:
                return None
            return self._value

    def _receive_loop(self) -> None:
        buffer = ""
        while self._running:
            try:
                with socket.create_connection((self._host, self._port), timeout=2.0) as sock:
                    sock.settimeout(1.0)
                    with self._lock:
                        self._connected = True
                    buffer = ""

                    while self._running:
                        chunk = sock.recv(1024)
                        if not chunk:
                            break
                        buffer += chunk.decode("ascii", errors="ignore")
                        while "\n" in buffer:
                            line, buffer = buffer.split("\n", 1)
                            self._store_value(line.strip())
            except OSError:
                with self._lock:
                    self._connected = False
                    self._value = None
                if self._running:
                    time.sleep(0.5)

    def _store_value(self, line: str) -> None:
        if not line:
            return
        try:
            value = float(line)
        except ValueError:
            return
        with self._lock:
            self._connected = True
            self._value = max(-1.0, min(1.0, value))
