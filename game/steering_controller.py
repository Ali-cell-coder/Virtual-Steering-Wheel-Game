"""Steering input abstraction for the driving game."""

from __future__ import annotations

import pygame

from constants import SOCKET_HOST, SOCKET_PORT, STEERING_DEADZONE
from steering_socket_client import SteeringSocketClient


class SteeringController:
    """
    Provides normalized steering input in the range [-1.0, +1.0].

    Uses steering values received over TCP when connected, otherwise falls back
    to keyboard input.
    """

    def __init__(self) -> None:
        self._socket_client = SteeringSocketClient(host=SOCKET_HOST, port=SOCKET_PORT)
        self._socket_client.start()

    def close(self) -> None:
        """Stop background socket communication."""
        self._socket_client.stop()

    def get_steering(self) -> float:
        """
        Return current steering value.

        -1.0 = full left
         0.0 = straight
        +1.0 = full right
        """
        socket_value = self._socket_client.get_value()
        if socket_value is not None:
            return self._apply_deadzone(socket_value)

        keys = pygame.key.get_pressed()
        steering = 0.0
        if keys[pygame.K_a]:
            steering -= 1.0
        if keys[pygame.K_d]:
            steering += 1.0
        return self._apply_deadzone(steering)

    @staticmethod
    def _apply_deadzone(value: float) -> float:
        if abs(value) < STEERING_DEADZONE:
            return 0.0
        return value
