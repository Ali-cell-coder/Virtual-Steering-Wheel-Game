"""Steering angle calibration and smoothing."""

from __future__ import annotations

import time
from dataclasses import dataclass


def normalize_angle_deg(angle_deg: float) -> float:
    """Wrap angle into [-180, 180] degrees."""
    normalized = angle_deg % 360.0
    if normalized > 180.0:
        normalized -= 360.0
    return normalized


@dataclass(frozen=True, slots=True)
class SteeringState:
    """Processed steering angles for rendering and debug display."""

    raw_angle_deg: float | None
    calibrated_angle_deg: float | None
    smoothed_angle_deg: float | None


class SteeringController:
    """Applies neutral calibration and EMA smoothing to steering angles."""

    def __init__(self, smoothing_alpha: float = 0.2) -> None:
        self._smoothing_alpha = float(smoothing_alpha)
        self._neutral_angle_deg: float | None = None
        self._smoothed_angle_deg: float | None = None
        self._calibration_message_until: float | None = None

    def calibrate(self, raw_angle_deg: float) -> None:
        """Store the current angle as the neutral steering position."""
        self._neutral_angle_deg = raw_angle_deg
        self._smoothed_angle_deg = 0.0
        self._calibration_message_until = time.perf_counter() + 2.0

    def process(self, raw_angle_deg: float | None) -> SteeringState:
        """Convert a raw angle into calibrated and smoothed steering values."""
        if raw_angle_deg is None:
            self._smoothed_angle_deg = None
            return SteeringState(None, None, None)

        calibrated_angle_deg = self._to_calibrated_angle(raw_angle_deg)
        self._smoothed_angle_deg = self._apply_ema(calibrated_angle_deg)

        return SteeringState(
            raw_angle_deg=raw_angle_deg,
            calibrated_angle_deg=calibrated_angle_deg,
            smoothed_angle_deg=self._smoothed_angle_deg,
        )

    def should_show_calibration_message(self) -> bool:
        """Return True while the post-calibration message should be visible."""
        if self._calibration_message_until is None:
            return False
        return time.perf_counter() < self._calibration_message_until

    def _to_calibrated_angle(self, raw_angle_deg: float) -> float:
        if self._neutral_angle_deg is None:
            return raw_angle_deg
        return normalize_angle_deg(raw_angle_deg - self._neutral_angle_deg)

    def _apply_ema(self, calibrated_angle_deg: float) -> float:
        if self._smoothed_angle_deg is None:
            return calibrated_angle_deg
        return (
            self._smoothing_alpha * calibrated_angle_deg
            + (1.0 - self._smoothing_alpha) * self._smoothed_angle_deg
        )
