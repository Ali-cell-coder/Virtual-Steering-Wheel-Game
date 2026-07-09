"""Steering wheel overlay rendering."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


class SteeringWheelOverlay:
    """Renders a rotating, semi-transparent steering wheel overlay."""

    def __init__(
        self,
        image_path: Path,
        alpha: float = 0.78,
        relative_size: float = 0.53,
        vertical_offset_px: int = 70,
    ) -> None:
        self._image_path = image_path
        self._alpha = float(np.clip(alpha, 0.0, 1.0))
        self._relative_size = relative_size
        self._vertical_offset_px = vertical_offset_px
        self._wheel_image_rgba = self._load_wheel_image()

    def draw(self, frame_bgr: np.ndarray, steering_angle_deg: float | None) -> None:
        """Draw steering wheel centered on frame, rotated by steering angle."""
        if self._wheel_image_rgba is None:
            return

        frame_height, frame_width = frame_bgr.shape[:2]
        target_size = max(120, int(min(frame_width, frame_height) * self._relative_size))

        wheel_rgba = cv2.resize(
            self._wheel_image_rgba,
            (target_size, target_size),
            interpolation=cv2.INTER_AREA,
        )
        angle = 0.0 if steering_angle_deg is None else -steering_angle_deg
        rotated_wheel = self._rotate_rgba(wheel_rgba, angle)
        self._blend_rgba_centered(frame_bgr, rotated_wheel, self._vertical_offset_px)

    def _load_wheel_image(self) -> np.ndarray | None:
        """Load steering wheel PNG as RGBA if available and valid."""
        if not self._image_path.exists():
            return None

        image = cv2.imread(str(self._image_path), cv2.IMREAD_UNCHANGED)
        if image is None:
            return None

        if image.ndim != 3:
            return None

        if image.shape[2] == 4:
            return image
        if image.shape[2] == 3:
            alpha_channel = np.full(image.shape[:2], 255, dtype=np.uint8)
            return np.dstack((image, alpha_channel))
        return None

    def _rotate_rgba(self, wheel_rgba: np.ndarray, angle_deg: float) -> np.ndarray:
        """Rotate wheel image around its exact center."""
        height, width = wheel_rgba.shape[:2]
        center = (width / 2.0, height / 2.0)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
        return cv2.warpAffine(
            wheel_rgba,
            rotation_matrix,
            (width, height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0, 0),
        )

    def _blend_rgba_centered(
        self, frame_bgr: np.ndarray, wheel_rgba: np.ndarray, center_offset_y: int = 0
    ) -> None:
        """Alpha blend an RGBA wheel image into the frame center."""
        frame_h, frame_w = frame_bgr.shape[:2]
        wheel_h, wheel_w = wheel_rgba.shape[:2]
        center_x = frame_w // 2
        center_y = (frame_h // 2) + center_offset_y

        x1 = max(center_x - wheel_w // 2, 0)
        y1 = max(center_y - wheel_h // 2, 0)
        x2 = min(x1 + wheel_w, frame_w)
        y2 = min(y1 + wheel_h, frame_h)

        roi_w = x2 - x1
        roi_h = y2 - y1
        if roi_w <= 0 or roi_h <= 0:
            return

        wheel_crop = wheel_rgba[:roi_h, :roi_w]
        wheel_bgr = wheel_crop[:, :, :3].astype(np.float32)
        wheel_alpha = (wheel_crop[:, :, 3].astype(np.float32) / 255.0) * self._alpha
        wheel_alpha = wheel_alpha[:, :, None]

        roi = frame_bgr[y1:y2, x1:x2].astype(np.float32)
        blended = (wheel_alpha * wheel_bgr) + ((1.0 - wheel_alpha) * roi)
        frame_bgr[y1:y2, x1:x2] = blended.astype(np.uint8)
