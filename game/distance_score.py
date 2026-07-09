"""Distance score tracking and display."""

from __future__ import annotations

import pygame

from constants import (
    COLOR_TEXT,
    DISTANCE_METERS_PER_SECOND_BASE,
    HUD_LINE_SPACING,
    HUD_MARGIN_X,
    HUD_MARGIN_Y,
)
from game_speed import GameSpeed
from high_score import HighScore


class DistanceScore:
    """Tracks how far the player has traveled in meters."""

    def __init__(self, game_speed: GameSpeed, high_score: HighScore) -> None:
        self._game_speed = game_speed
        self._high_score = high_score
        self._distance_meters = 0.0

    def update(self, dt: float) -> None:
        meters_per_second = DISTANCE_METERS_PER_SECOND_BASE * self._game_speed.multiplier
        self._distance_meters += meters_per_second * dt
        self._high_score.update_if_better(self.meters)

    def reset(self) -> None:
        self._distance_meters = 0.0

    @property
    def meters(self) -> int:
        return int(self._distance_meters)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        distance_label = font.render(f"Distance: {self.meters} m", True, COLOR_TEXT)
        surface.blit(distance_label, (HUD_MARGIN_X, HUD_MARGIN_Y))

        high_score_y = HUD_MARGIN_Y + distance_label.get_height() + HUD_LINE_SPACING
        high_score_label = font.render(
            f"High Score: {self._high_score.meters} m",
            True,
            COLOR_TEXT,
        )
        surface.blit(high_score_label, (HUD_MARGIN_X, high_score_y))
