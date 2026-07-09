"""Shared utility helpers."""

from __future__ import annotations

import time

import cv2
import numpy as np

from config import UiConfig


class FpsCounter:
    """Tracks and returns smoothed FPS."""

    def __init__(self, smoothing: float = 0.9) -> None:
        self._smoothing = smoothing
        self._last_time = time.perf_counter()
        self._fps = 0.0

    def tick(self) -> float:
        """Update FPS value and return current smoothed FPS."""
        now = time.perf_counter()
        delta = max(now - self._last_time, 1e-6)
        instant_fps = 1.0 / delta
        self._fps = (
            self._smoothing * self._fps + (1.0 - self._smoothing) * instant_fps
            if self._fps > 0.0
            else instant_fps
        )
        self._last_time = now
        return self._fps


def draw_fps(frame_bgr: np.ndarray, fps: float, ui_config: UiConfig) -> None:
    """Draw FPS text on the frame in-place."""
    cv2.putText(
        frame_bgr,
        f"FPS: {fps:.1f}",
        ui_config.fps_position,
        cv2.FONT_HERSHEY_SIMPLEX,
        ui_config.font_scale,
        ui_config.font_color_bgr,
        ui_config.font_thickness,
        cv2.LINE_AA,
    )
