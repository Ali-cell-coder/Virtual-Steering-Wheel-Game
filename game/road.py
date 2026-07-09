"""Endless scrolling road with lane boundaries."""

from __future__ import annotations

import pygame

from constants import (
    COLOR_LANE,
    COLOR_ROAD,
    COLOR_ROAD_EDGE,
    LANE_LINE_GAP,
    LANE_LINE_LENGTH,
    LANE_LINE_WIDTH,
    ROAD_SCROLL_SPEED,
    ROAD_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


class Road:
    """Renders a vertically scrolling road and validates on-road position."""

    def __init__(self) -> None:
        self._scroll_offset = 0.0
        self.left = (SCREEN_WIDTH - ROAD_WIDTH) // 2
        self.right = self.left + ROAD_WIDTH

    def update(self, dt: float, scroll_speed: float | None = None) -> None:
        speed = ROAD_SCROLL_SPEED if scroll_speed is None else scroll_speed
        self._scroll_offset = (self._scroll_offset + speed * dt) % (
            LANE_LINE_LENGTH + LANE_LINE_GAP
        )

    def reset(self) -> None:
        self._scroll_offset = 0.0

    def is_on_road(self, car_rect: pygame.Rect) -> bool:
        car_left = car_rect.left
        car_right = car_rect.right
        return car_left >= self.left and car_right <= self.right

    def draw(self, surface: pygame.Surface) -> None:
        road_rect = pygame.Rect(self.left, 0, ROAD_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(surface, COLOR_ROAD, road_rect)
        pygame.draw.line(surface, COLOR_ROAD_EDGE, (self.left, 0), (self.left, SCREEN_HEIGHT), 6)
        pygame.draw.line(
            surface, COLOR_ROAD_EDGE, (self.right, 0), (self.right, SCREEN_HEIGHT), 6
        )

        center_x = SCREEN_WIDTH // 2
        y = -LANE_LINE_LENGTH
        while y < SCREEN_HEIGHT + LANE_LINE_LENGTH:
            draw_y = int(y + self._scroll_offset)
            pygame.draw.line(
                surface,
                COLOR_LANE,
                (center_x, draw_y),
                (center_x, draw_y + LANE_LINE_LENGTH),
                LANE_LINE_WIDTH,
            )
            y += LANE_LINE_LENGTH + LANE_LINE_GAP
