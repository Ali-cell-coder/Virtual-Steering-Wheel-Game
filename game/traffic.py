"""Traffic spawning and management."""

from __future__ import annotations

import random

import pygame

from car import Car
from constants import (
    GAME_START_GRACE_SECONDS,
    TRAFFIC_CAR_HEIGHT,
    TRAFFIC_CAR_SPEED,
    TRAFFIC_CAR_WIDTH,
    TRAFFIC_MAX_SPAWN_ATTEMPTS,
    TRAFFIC_MIN_VERTICAL_GAP,
    TRAFFIC_PLAYER_SAFE_GAP,
    TRAFFIC_SPAWN_Y,
)
from game_speed import GameSpeed
from lanes import car_x_for_lane, get_lane_centers
from road import Road
from traffic_car import TrafficCar
from traffic_density import TrafficDensity
from traffic_sprites import TrafficSpriteCatalog


class TrafficManager:
    """Spawns, updates, and recycles enemy traffic cars."""

    def __init__(self, road: Road, player_car: Car) -> None:
        self._road = road
        self._player_car = player_car
        self._sprite_catalog = TrafficSpriteCatalog()
        self._cars: list[TrafficCar] = []
        self._lane_spawn_counts = [0, 0, 0]
        self._elapsed_time = 0.0
        self._spawn_timer = 0.0
        self._traffic_speed = TRAFFIC_CAR_SPEED
        self._seed_initial_traffic()

    def update(self, dt: float, game_speed: GameSpeed | None = None) -> None:
        self._elapsed_time += dt
        self._traffic_speed = game_speed.traffic_speed if game_speed else TRAFFIC_CAR_SPEED
        density = TrafficDensity.multiplier(self._elapsed_time)

        for car in self._cars:
            car.speed = self._traffic_speed
            car.update(dt)

        active_before = len(self._cars)
        self._cars = [car for car in self._cars if not car.is_off_screen()]
        removed_count = active_before - len(self._cars)

        max_cars = TrafficDensity.max_cars_on_screen(self._elapsed_time, density)
        spawn_interval = TrafficDensity.spawn_interval(self._elapsed_time, density)

        self._spawn_timer += dt
        while self._spawn_timer >= spawn_interval and len(self._cars) < max_cars:
            if not self._try_spawn():
                break
            self._spawn_timer -= spawn_interval

        for _ in range(removed_count):
            if len(self._cars) >= max_cars:
                break
            self._try_spawn()

    def check_collision(self, player_rect: pygame.Rect) -> bool:
        return any(player_rect.colliderect(car.get_rect()) for car in self._cars)

    def draw(self, surface: pygame.Surface) -> None:
        for car in self._cars:
            car.draw(surface)

    def reset(self) -> None:
        """Clear all traffic and restart spawning with the grace period."""
        self._cars.clear()
        self._lane_spawn_counts = [0, 0, 0]
        self._elapsed_time = 0.0
        self._spawn_timer = 0.0
        self._traffic_speed = TRAFFIC_CAR_SPEED
        self._seed_initial_traffic()

    def _in_grace_period(self) -> bool:
        return self._elapsed_time < GAME_START_GRACE_SECONDS

    def _seed_initial_traffic(self) -> None:
        density = TrafficDensity.multiplier(self._elapsed_time)
        target_count = TrafficDensity.initial_car_count(self._elapsed_time, density)
        spawn_y = self._preferred_spawn_y()

        for _ in range(target_count):
            if not self._try_spawn_at(spawn_y):
                break
            spawn_y += TRAFFIC_CAR_HEIGHT + TRAFFIC_MIN_VERTICAL_GAP

    def _try_spawn(self) -> bool:
        for _ in range(TRAFFIC_MAX_SPAWN_ATTEMPTS):
            if self._try_spawn_at(self._preferred_spawn_y()):
                return True
        return False

    def _try_spawn_at(self, preferred_y: float) -> bool:
        lane_centers = self._lane_centers()
        lane_order = self._lane_spawn_order(lane_centers)

        for lane_index, lane_center in lane_order:
            spawn_y = self._find_safe_spawn_y_for_lane(lane_index, preferred_y)
            if spawn_y is None:
                continue

            spawn_x = car_x_for_lane(lane_center, TRAFFIC_CAR_WIDTH)
            if self._conflicts_with_player(spawn_x, spawn_y):
                continue

            sprite = self._sprite_catalog.random_sprite()
            self._cars.append(TrafficCar(spawn_x, spawn_y, sprite=sprite))
            self._lane_spawn_counts[lane_index] += 1
            return True

        return False

    def _preferred_spawn_y(self) -> float:
        if self._in_grace_period():
            return self._grace_min_spawn_y()
        return float(TRAFFIC_SPAWN_Y)

    def _grace_min_spawn_y(self) -> float:
        """Spawn far enough up the road that traffic cannot reach the player during grace."""
        player_rect = self._player_car.get_rect()
        grace_remaining = max(0.0, GAME_START_GRACE_SECONDS - self._elapsed_time)
        required_gap = grace_remaining * self._traffic_speed + TRAFFIC_PLAYER_SAFE_GAP
        return player_rect.top - required_gap - TRAFFIC_CAR_HEIGHT

    def _lane_spawn_order(self, lane_centers: list[float]) -> list[tuple[int, float]]:
        min_count = min(self._lane_spawn_counts)
        least_used = [
            (index, lane_center)
            for index, lane_center in enumerate(lane_centers)
            if self._lane_spawn_counts[index] == min_count
        ]
        random.shuffle(least_used)
        return least_used

    def _conflicts_with_player(self, spawn_x: float, spawn_y: float) -> bool:
        player_rect = self._player_car.get_rect()
        spawn_rect = pygame.Rect(
            int(spawn_x),
            int(spawn_y),
            TRAFFIC_CAR_WIDTH,
            TRAFFIC_CAR_HEIGHT,
        )

        if spawn_rect.colliderect(player_rect):
            return True

        gap_above_player = player_rect.top - spawn_rect.bottom
        if self._in_grace_period():
            grace_remaining = max(0.0, GAME_START_GRACE_SECONDS - self._elapsed_time)
            required_gap = grace_remaining * self._traffic_speed + TRAFFIC_PLAYER_SAFE_GAP
            return gap_above_player < required_gap

        if not self._same_lane(spawn_x, player_rect):
            return False

        return gap_above_player < TRAFFIC_PLAYER_SAFE_GAP

    def _same_lane(self, spawn_x: float, player_rect: pygame.Rect) -> bool:
        return self._lane_index_for_x(spawn_x) == self._lane_index_for_x(
            player_rect.centerx - TRAFFIC_CAR_WIDTH / 2.0
        )

    def _lane_index_for_x(self, car_x: float) -> int:
        car_center_x = car_x + TRAFFIC_CAR_WIDTH / 2.0
        lane_centers = self._lane_centers()
        return min(
            range(len(lane_centers)),
            key=lambda index: abs(lane_centers[index] - car_center_x),
        )

    def _find_safe_spawn_y_for_lane(self, lane_index: int, preferred_y: float) -> float | None:
        spawn_y = preferred_y
        for car in self._cars:
            if self._lane_index_for_x(car.x) != lane_index:
                continue
            if abs(car.y - spawn_y) < TRAFFIC_MIN_VERTICAL_GAP:
                spawn_y = min(spawn_y, car.y - TRAFFIC_MIN_VERTICAL_GAP)

        if self._in_grace_period() and spawn_y > preferred_y:
            spawn_y = preferred_y

        if spawn_y < TRAFFIC_SPAWN_Y - TRAFFIC_CAR_HEIGHT * 10:
            return None

        if not self._has_safe_lane_gap(lane_index, spawn_y):
            return None

        return spawn_y

    def _has_safe_lane_gap(self, lane_index: int, spawn_y: float) -> bool:
        for car in self._cars:
            if self._lane_index_for_x(car.x) != lane_index:
                continue
            if abs(car.y - spawn_y) < TRAFFIC_MIN_VERTICAL_GAP:
                return False
        return True

    def _lane_centers(self) -> list[float]:
        return get_lane_centers(self._road)
