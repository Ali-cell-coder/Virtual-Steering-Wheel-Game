"""Game sound effects."""

from __future__ import annotations

from pathlib import Path

import pygame

CRASH_SOUND_PATH = Path(__file__).resolve().parent / "assets" / "sounds" / "crash.wav"


class CrashSound:
    """Plays a one-shot crash sound effect."""

    def __init__(self) -> None:
        self._sound: pygame.mixer.Sound | None = None
        self._load()

    def play(self) -> None:
        if self._sound is None:
            return
        self._sound.play()

    def _load(self) -> None:
        if not CRASH_SOUND_PATH.exists():
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self._sound = pygame.mixer.Sound(str(CRASH_SOUND_PATH))
        except pygame.error:
            self._sound = None
