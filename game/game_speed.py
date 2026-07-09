"""Progressive game speed scaling over time."""

from __future__ import annotations

from constants import (
    GAME_SPEED_RAMP_SECONDS,
    MAX_SPEED_MULTIPLIER,
    ROAD_SCROLL_SPEED,
    TRAFFIC_CAR_SPEED,
)


class GameSpeed:
    """Smoothly increases road and traffic speed while the player survives."""

    def __init__(self) -> None:
        self._elapsed_time = 0.0

    def update(self, dt: float) -> None:
        self._elapsed_time += dt

    def reset(self) -> None:
        self._elapsed_time = 0.0

    @property
    def multiplier(self) -> float:
        progress = min(1.0, self._elapsed_time / GAME_SPEED_RAMP_SECONDS)
        smooth_progress = progress * progress * (3.0 - 2.0 * progress)
        return 1.0 + (MAX_SPEED_MULTIPLIER - 1.0) * smooth_progress

    @property
    def road_scroll_speed(self) -> float:
        return ROAD_SCROLL_SPEED * self.multiplier

    @property
    def traffic_speed(self) -> float:
        return TRAFFIC_CAR_SPEED * self.multiplier
