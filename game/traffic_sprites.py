"""Loads and caches traffic car sprites from disk."""

from __future__ import annotations

import random
from pathlib import Path

import pygame

from constants import ROAD_WIDTH, TRAFFIC_CAR_HEIGHT, TRAFFIC_CAR_WIDTH

TRAFFIC_ASSETS_DIR = Path(__file__).resolve().parent / "assets" / "traffic"


class TrafficSpriteCatalog:
    """Discovers, loads, and serves scaled traffic car sprites."""

    def __init__(self) -> None:
        self._sprites = self._load_all_sprites()

    def random_sprite(self) -> pygame.Surface | None:
        if not self._sprites:
            return None
        return random.choice(self._sprites)

    def _load_all_sprites(self) -> list[pygame.Surface]:
        if not TRAFFIC_ASSETS_DIR.is_dir():
            return []

        sprites: list[pygame.Surface] = []
        for image_path in sorted(TRAFFIC_ASSETS_DIR.glob("*.png")):
            sprite = self._load_sprite(image_path)
            if sprite is not None:
                sprites.append(sprite)
        return sprites

    def _load_sprite(self, image_path: Path) -> pygame.Surface | None:
        try:
            image = pygame.image.load(str(image_path)).convert_alpha()
        except pygame.error:
            return None

        return self._scale_to_uniform_size(image)

    def _scale_to_uniform_size(self, image: pygame.Surface) -> pygame.Surface:
        """Scale every sprite to a consistent on-screen size, preserving aspect ratio."""
        image_width, image_height = image.get_size()
        if image_width <= 0 or image_height <= 0:
            return image

        max_width = min(TRAFFIC_CAR_WIDTH, int(ROAD_WIDTH * 0.14))
        target_height = TRAFFIC_CAR_HEIGHT

        scale = target_height / image_height
        if image_width * scale > max_width:
            scale = max_width / image_width

        scaled_width = max(1, int(image_width * scale))
        scaled_height = max(1, int(image_height * scale))
        return pygame.transform.smoothscale(image, (scaled_width, scaled_height))
