"""TCP server for broadcasting normalized steering values to the game."""

from __future__ import annotations

import socket
import threading
import time


class SteeringSocketServer:
    """Sends normalized steering values to a connected game client."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 5555,
        send_rate_hz: int = 60,
    ) -> None:
        self._host = host
        self._port = port
        self._send_interval = 1.0 / send_rate_hz
        self._latest_value = 0.0
        self._lock = threading.Lock()
        self._running = False
        self._server_socket: socket.socket | None = None
        self._client_socket: socket.socket | None = None
        self._accept_thread: threading.Thread | None = None
        self._send_thread: threading.Thread | None = None

    def start(self) -> None:
        """Start listening for a game client connection."""
        if self._running:
            return

        self._running = True
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self._host, self._port))
        self._server_socket.listen(1)
        self._server_socket.settimeout(1.0)

        self._accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._send_thread = threading.Thread(target=self._send_loop, daemon=True)
        self._accept_thread.start()
        self._send_thread.start()

    def stop(self) -> None:
        """Shut down the server and close active connections."""
        self._running = False
        self._close_client_socket()
        if self._server_socket is not None:
            try:
                self._server_socket.close()
            except OSError:
                pass
            self._server_socket = None

    def send_steering(self, value: float) -> None:
        """Store the latest normalized steering value for transmission."""
        with self._lock:
            self._latest_value = max(-1.0, min(1.0, value))

    def _accept_loop(self) -> None:
        while self._running and self._server_socket is not None:
            try:
                client_socket, _ = self._server_socket.accept()
                client_socket.settimeout(1.0)
                self._close_client_socket()
                self._client_socket = client_socket
            except TimeoutError:
                continue
            except OSError:
                if self._running:
                    time.sleep(0.1)

    def _send_loop(self) -> None:
        while self._running:
            time.sleep(self._send_interval)
            with self._lock:
                value = self._latest_value
                client_socket = self._client_socket

            if client_socket is None:
                continue

            try:
                payload = f"{value:.4f}\n".encode("ascii")
                client_socket.sendall(payload)
            except OSError:
                self._close_client_socket()

    def _close_client_socket(self) -> None:
        if self._client_socket is not None:
            try:
                self._client_socket.close()
            except OSError:
                pass
            self._client_socket = None
