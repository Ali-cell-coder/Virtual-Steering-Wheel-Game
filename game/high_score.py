"""Persistent high score storage."""

from __future__ import annotations

from pathlib import Path

HIGH_SCORE_PATH = Path(__file__).resolve().parent / "data" / "high_score.txt"


class HighScore:
    """Loads, updates, and saves the best distance achieved."""

    def __init__(self) -> None:
        self._meters = self._load()

    @property
    def meters(self) -> int:
        return self._meters

    def update_if_better(self, distance_meters: int) -> None:
        if distance_meters > self._meters:
            self._meters = distance_meters
            self._save(self._meters)

    def _load(self) -> int:
        try:
            if HIGH_SCORE_PATH.exists():
                return max(0, int(HIGH_SCORE_PATH.read_text(encoding="utf-8").strip()))
        except (OSError, ValueError):
            pass

        self._save(0)
        return 0

    def _save(self, meters: int) -> None:
        HIGH_SCORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        HIGH_SCORE_PATH.write_text(str(meters), encoding="utf-8")
