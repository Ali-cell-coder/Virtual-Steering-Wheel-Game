"""Camera management module."""

from __future__ import annotations

import cv2
import numpy as np

from config import CameraConfig


class CameraError(RuntimeError):
    """Raised when camera operations fail."""


class CameraStream:
    """Encapsulates webcam lifecycle and frame retrieval."""

    def __init__(self, config: CameraConfig) -> None:
        self._config = config
        self._capture: cv2.VideoCapture | None = None

    def open(self) -> None:
        """Open and configure the webcam."""
        self._capture = cv2.VideoCapture(self._config.device_index)
        if not self._capture.isOpened():
            raise CameraError(
                f"Unable to open camera at index {self._config.device_index}. "
                "Check device availability and permissions."
            )

        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self._config.width)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self._config.height)

    def read(self) -> np.ndarray:
        """Read a frame from the webcam."""
        if self._capture is None:
            raise CameraError("Camera has not been opened yet.")

        ok, frame = self._capture.read()
        if not ok or frame is None:
            raise CameraError("Failed to read frame from camera stream.")
        return frame

    def release(self) -> None:
        """Release camera resources."""
        if self._capture is not None:
            self._capture.release()
            self._capture = None
