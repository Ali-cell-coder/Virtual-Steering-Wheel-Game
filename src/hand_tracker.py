"""Hand tracking module powered by MediaPipe."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from config import HandTrackingConfig

try:
    # MediaPipe versions that expose solutions at top-level package.
    from mediapipe import solutions as mp_solutions
except ImportError:
    # MediaPipe versions where solutions live under mediapipe.python.
    from mediapipe.python import solutions as mp_solutions


@dataclass(frozen=True, slots=True)
class HandObservation:
    """Computed, render-ready hand data for downstream modules."""

    label: str
    center: tuple[int, int]


class HandTracker:
    """Detects and renders hands using MediaPipe Hands."""

    def __init__(self, config: HandTrackingConfig) -> None:
        self._mp_hands = mp_solutions.hands
        self._mp_drawing = mp_solutions.drawing_utils
        self._mp_drawing_styles = mp_solutions.drawing_styles

        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=config.max_num_hands,
            min_detection_confidence=config.min_detection_confidence,
            min_tracking_confidence=config.min_tracking_confidence,
        )

    def process(self, frame_bgr: np.ndarray) -> object:
        """Run hand detection on a BGR frame."""
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        frame_rgb.flags.writeable = False
        results = self._hands.process(frame_rgb)
        return results

    def draw(self, frame_bgr: np.ndarray, results: object) -> None:
        """Draw hand landmarks and connections on the frame in-place."""
        if not getattr(results, "multi_hand_landmarks", None):
            return

        for hand_landmarks in results.multi_hand_landmarks:
            self._mp_drawing.draw_landmarks(
                frame_bgr,
                hand_landmarks,
                self._mp_hands.HAND_CONNECTIONS,
                self._mp_drawing_styles.get_default_hand_landmarks_style(),
                self._mp_drawing_styles.get_default_hand_connections_style(),
            )

    def extract_observations(self, frame_bgr: np.ndarray, results: object) -> list[HandObservation]:
        """Extract handedness and center coordinates for each detected hand."""
        landmarks_list = getattr(results, "multi_hand_landmarks", None)
        handedness_list = getattr(results, "multi_handedness", None)
        if not landmarks_list:
            return []

        frame_height, frame_width = frame_bgr.shape[:2]
        observations: list[HandObservation] = []

        for idx, hand_landmarks in enumerate(landmarks_list):
            x_values = [lm.x for lm in hand_landmarks.landmark]
            y_values = [lm.y for lm in hand_landmarks.landmark]

            center_x = int(np.clip(np.mean(x_values) * frame_width, 0, frame_width - 1))
            center_y = int(np.clip(np.mean(y_values) * frame_height, 0, frame_height - 1))

            label = "UNKNOWN"
            if handedness_list and idx < len(handedness_list):
                classifications = getattr(handedness_list[idx], "classification", [])
                if classifications:
                    label = str(classifications[0].label).upper()

            observations.append(HandObservation(label=label, center=(center_x, center_y)))

        return observations

    def close(self) -> None:
        """Release MediaPipe resources."""
        self._hands.close()
