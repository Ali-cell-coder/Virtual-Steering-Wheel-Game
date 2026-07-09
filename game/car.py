"""Player car entity."""

from __future__ import annotations

from pathlib import Path

import pygame

from constants import (
    CAR_HEIGHT,
    CAR_MOVE_SPEED,
    CAR_WIDTH,
    CAR_Y_OFFSET,
    ROAD_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)

CAR_IMAGE_PATH = Path(__file__).resolve().parent / "assets" / "car-truck1.png"


class Car:
    """Represents the player-controlled car."""

    def __init__(self, start_lane_center_x: float | None = None) -> None:
        self.width = CAR_WIDTH
        self.height = CAR_HEIGHT
        self.y = SCREEN_HEIGHT - CAR_Y_OFFSET - self.height
        if start_lane_center_x is None:
            self.x = (SCREEN_WIDTH - self.width) / 2.0
        else:
            self.x = start_lane_center_x - self.width / 2.0
        self._image = self._load_car_image()

    def update(self, steering: float, dt: float) -> None:
        """Move the car horizontally based on normalized steering input."""
        self.x += steering * CAR_MOVE_SPEED * dt
        self.x = max(0.0, min(self.x, SCREEN_WIDTH - self.width))

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def reset(self) -> None:
        """Return the player to the default center-lane starting position."""
        self.x = (SCREEN_WIDTH - self.width) / 2.0
        self.y = SCREEN_HEIGHT - CAR_Y_OFFSET - self.height

    def draw(self, surface: pygame.Surface) -> None:
        if self._image is None:
            return

        body = self.get_rect()
        image_rect = self._image.get_rect(center=body.center)
        surface.blit(self._image, image_rect)

    def _load_car_image(self) -> pygame.Surface | None:
        """Load and scale the player sprite, preserving transparency."""
        if not CAR_IMAGE_PATH.exists():
            return None

        try:
            image = pygame.image.load(str(CAR_IMAGE_PATH)).convert_alpha()
        except pygame.error:
            return None

        return self._scale_to_uniform_size(image)

    def _scale_to_uniform_size(self, image: pygame.Surface) -> pygame.Surface:
        """Match traffic car scaling so the player sprite fits naturally on the road."""
        image_width, image_height = image.get_size()
        if image_width <= 0 or image_height <= 0:
            return image

        max_width = min(CAR_WIDTH, int(ROAD_WIDTH * 0.14))
        target_height = CAR_HEIGHT

        scale = target_height / image_height
        if image_width * scale > max_width:
            scale = max_width / image_width

        scaled_width = max(1, int(image_width * scale))
        scaled_height = max(1, int(image_height * scale))
        return pygame.transform.smoothscale(image, (scaled_width, scaled_height))
