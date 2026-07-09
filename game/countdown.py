"""Pre-game start countdown overlay."""

from __future__ import annotations

import pygame

from constants import COLOR_TEXT, COUNTDOWN_STEP_SECONDS, SCREEN_HEIGHT, SCREEN_WIDTH

_COUNTDOWN_LABELS = ("3", "2", "1", "GO!")


class StartCountdown:
    """Displays a 3-2-1-GO countdown before gameplay begins."""

    def __init__(self) -> None:
        self._elapsed_time = 0.0
        self._active = True

    @property
    def is_active(self) -> bool:
        return self._active

    def reset(self) -> None:
        self._elapsed_time = 0.0
        self._active = True

    def update(self, dt: float) -> None:
        if not self._active:
            return

        self._elapsed_time += dt
        if self._elapsed_time >= COUNTDOWN_STEP_SECONDS * len(_COUNTDOWN_LABELS):
            self._active = False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        label = self._current_label()
        if label is None:
            return

        text = font.render(label, True, COLOR_TEXT)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        surface.blit(text, text_rect)

    def _current_label(self) -> str | None:
        if not self._active:
            return None

        step_index = int(self._elapsed_time / COUNTDOWN_STEP_SECONDS)
        if step_index >= len(_COUNTDOWN_LABELS):
            return None
        return _COUNTDOWN_LABELS[step_index]
