"""Core game loop and state management."""

from __future__ import annotations

import sys

import pygame

from car import Car
from constants import (
    COLOR_BACKGROUND,
    COLOR_GAME_OVER,
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from countdown import StartCountdown
from distance_score import DistanceScore
from game_speed import GameSpeed
from high_score import HighScore
from road import Road
from sound_effects import CrashSound
from steering_controller import SteeringController
from traffic import TrafficManager
from ui import RestartButton


class GameEngine:
    """Coordinates update, rendering, and game state."""

    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.init()
        self._screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Virtual Steering Wheel - Driving Game")
        self._clock = pygame.time.Clock()
        self._font = pygame.font.SysFont("consolas", 28)
        self._game_over_font = pygame.font.SysFont("consolas", 72, bold=True)
        self._countdown_font = pygame.font.SysFont("consolas", 96, bold=True)
        self._button_font = pygame.font.SysFont("consolas", 32, bold=True)

        self._steering = SteeringController()
        self._road = Road()
        self._car = Car()
        self._game_speed = GameSpeed()
        self._high_score = HighScore()
        self._distance_score = DistanceScore(self._game_speed, self._high_score)
        self._crash_sound = CrashSound()
        self._traffic = TrafficManager(self._road, self._car)
        self._countdown = StartCountdown()
        self._restart_button = RestartButton(self._button_font)
        self._running = True
        self._game_over = False

    def run(self) -> None:
        try:
            while self._running:
                dt = self._clock.tick(FPS) / 1000.0
                self._handle_events()
                self._update(dt)
                self._render()
        finally:
            self._steering.close()
            pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._running = False
            elif self._game_over and self._restart_button.handle_event(event):
                self._restart_game()

    def _restart_game(self) -> None:
        self._car.reset()
        self._traffic.reset()
        self._road.reset()
        self._game_speed.reset()
        self._distance_score.reset()
        self._countdown.reset()
        self._game_over = False

    def _update(self, dt: float) -> None:
        if self._game_over:
            return

        if self._countdown.is_active:
            self._countdown.update(dt)
            return

        self._game_speed.update(dt)
        self._distance_score.update(dt)
        self._road.update(dt, self._game_speed.road_scroll_speed)
        self._traffic.update(dt, self._game_speed)
        steering = self._steering.get_steering()
        self._car.update(steering, dt)

        player_rect = self._car.get_rect()
        if not self._road.is_on_road(player_rect) or self._traffic.check_collision(player_rect):
            self._trigger_game_over()

    def _trigger_game_over(self) -> None:
        if self._game_over:
            return

        self._high_score.update_if_better(self._distance_score.meters)
        self._crash_sound.play()
        self._game_over = True

    def _render(self) -> None:
        self._screen.fill(COLOR_BACKGROUND)
        self._road.draw(self._screen)
        self._traffic.draw(self._screen)
        self._car.draw(self._screen)

        self._distance_score.draw(self._screen, self._font)

        if self._countdown.is_active:
            self._countdown.draw(self._screen, self._countdown_font)

        if self._game_over:
            game_over_text = self._game_over_font.render("GAME OVER", True, COLOR_GAME_OVER)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self._screen.blit(game_over_text, text_rect)
            self._restart_button.draw(self._screen)

        pygame.display.flip()


def main() -> None:
    try:
        GameEngine().run()
    except pygame.error as exc:
        print(f"[GameError] {exc}", file=sys.stderr)
        pygame.quit()
        raise SystemExit(1) from exc
