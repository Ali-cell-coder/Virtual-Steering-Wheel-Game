"""Simple UI components for the driving game."""

from __future__ import annotations

import pygame

from constants import (
    COLOR_BUTTON,
    COLOR_BUTTON_BORDER,
    COLOR_BUTTON_HOVER,
    COLOR_TEXT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


class RestartButton:
    """Clickable restart button shown on the game over screen."""

    WIDTH = 220
    HEIGHT = 56

    def __init__(self, font: pygame.font.Font) -> None:
        self._font = font
        self._rect = pygame.Rect(0, 0, self.WIDTH, self.HEIGHT)
        self._rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)
        self._hovered = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self._rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        fill_color = COLOR_BUTTON_HOVER if self._hovered else COLOR_BUTTON
        pygame.draw.rect(surface, fill_color, self._rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_BUTTON_BORDER, self._rect, width=2, border_radius=10)

        label = self._font.render("Restart", True, COLOR_TEXT)
        label_rect = label.get_rect(center=self._rect.center)
        surface.blit(label, label_rect)
