"""Enemy traffic car entity."""

from __future__ import annotations

import pygame

from constants import (
    COLOR_TRAFFIC_CAR,
    COLOR_TRAFFIC_CAR_WINDOW,
    SCREEN_HEIGHT,
    TRAFFIC_CAR_HEIGHT,
    TRAFFIC_CAR_SPEED,
    TRAFFIC_CAR_WIDTH,
)


class TrafficCar:
    """A lane-following enemy car that moves downward."""

    def __init__(
        self,
        x: float,
        y: float,
        sprite: pygame.Surface | None = None,
        speed: float = TRAFFIC_CAR_SPEED,
    ) -> None:
        self.width = TRAFFIC_CAR_WIDTH
        self.height = TRAFFIC_CAR_HEIGHT
        self.x = x
        self.y = y
        self.speed = speed
        self._image = sprite

    def update(self, dt: float) -> None:
        self.y += self.speed * dt

    def is_off_screen(self) -> bool:
        return self.y > SCREEN_HEIGHT

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface: pygame.Surface) -> None:
        body = self.get_rect()
        if self._image is not None:
            image_rect = self._image.get_rect(center=body.center)
            surface.blit(self._image, image_rect)
            return

        pygame.draw.rect(surface, COLOR_TRAFFIC_CAR, body, border_radius=10)
        window = body.inflate(-16, -42)
        window.y += 8
        pygame.draw.rect(surface, COLOR_TRAFFIC_CAR_WINDOW, window, border_radius=6)
