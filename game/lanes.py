"""Lane layout helpers for player and traffic positioning."""

from __future__ import annotations

from constants import ROAD_WIDTH
from road import Road


def get_lane_centers(road: Road) -> list[float]:
    """Return x-center positions for the left, center, and right lanes."""
    return [
        road.left + ROAD_WIDTH * (1 / 6),
        road.left + ROAD_WIDTH * (1 / 2),
        road.left + ROAD_WIDTH * (5 / 6),
    ]


def get_center_lane(road: Road) -> float:
    """Return the x-center position of the middle lane."""
    return get_lane_centers(road)[1]


def car_x_for_lane(lane_center_x: float, car_width: float) -> float:
    """Convert a lane center to the top-left x position for a car."""
    return lane_center_x - car_width / 2.0
