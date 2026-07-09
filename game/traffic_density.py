"""Progressive traffic density scaling over time."""

from __future__ import annotations

from constants import (
    GAME_START_GRACE_SECONDS,
    TRAFFIC_DENSITY_LIGHT,
    TRAFFIC_DENSITY_MAX,
    TRAFFIC_DENSITY_RAMP_SECONDS,
    TRAFFIC_GRACE_MAX_ON_SCREEN,
    TRAFFIC_GRACE_SPAWN_INTERVAL,
    TRAFFIC_MAX_ON_SCREEN,
    TRAFFIC_MIN_SPAWN_INTERVAL,
)


class TrafficDensity:
    """Controls how often and how many traffic cars appear."""

    @staticmethod
    def multiplier(elapsed_time: float) -> float:
        if elapsed_time < GAME_START_GRACE_SECONDS:
            return TRAFFIC_DENSITY_LIGHT

        ramp_time = elapsed_time - GAME_START_GRACE_SECONDS
        progress = min(1.0, ramp_time / TRAFFIC_DENSITY_RAMP_SECONDS)
        smooth_progress = progress * progress * (3.0 - 2.0 * progress)
        return TRAFFIC_DENSITY_LIGHT + (TRAFFIC_DENSITY_MAX - TRAFFIC_DENSITY_LIGHT) * smooth_progress

    @staticmethod
    def max_cars_on_screen(elapsed_time: float, density: float) -> int:
        if elapsed_time < GAME_START_GRACE_SECONDS:
            return TRAFFIC_GRACE_MAX_ON_SCREEN

        density_range = TRAFFIC_DENSITY_MAX - TRAFFIC_DENSITY_LIGHT
        density_factor = (
            (density - TRAFFIC_DENSITY_LIGHT) / density_range if density_range > 0 else 1.0
        )
        car_span = TRAFFIC_MAX_ON_SCREEN - TRAFFIC_GRACE_MAX_ON_SCREEN
        return TRAFFIC_GRACE_MAX_ON_SCREEN + int(car_span * density_factor)

    @staticmethod
    def spawn_interval(elapsed_time: float, density: float) -> float:
        if elapsed_time < GAME_START_GRACE_SECONDS:
            return TRAFFIC_GRACE_SPAWN_INTERVAL

        density_span = max(TRAFFIC_DENSITY_LIGHT, TRAFFIC_DENSITY_MAX - TRAFFIC_DENSITY_LIGHT)
        density_factor = (density - TRAFFIC_DENSITY_LIGHT) / density_span
        return TRAFFIC_GRACE_SPAWN_INTERVAL - (
            (TRAFFIC_GRACE_SPAWN_INTERVAL - TRAFFIC_MIN_SPAWN_INTERVAL) * density_factor
        )

    @staticmethod
    def initial_car_count(elapsed_time: float, density: float) -> int:
        if elapsed_time < GAME_START_GRACE_SECONDS:
            return 2
        return max(2, int(2 + 4 * density))
