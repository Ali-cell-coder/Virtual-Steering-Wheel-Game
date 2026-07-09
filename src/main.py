"""Application entry point."""

from __future__ import annotations

import math
from pathlib import Path

import cv2
import numpy as np

from camera import CameraError, CameraStream
from config import AppConfig
from hand_tracker import HandObservation, HandTracker
from steering_controller import SteeringController, SteeringState
from steering_socket_server import SteeringSocketServer
from steering_wheel import SteeringWheelOverlay
from utils import FpsCounter, draw_fps


class VirtualSteeringWheelApp:
    """Coordinates camera capture, hand tracking, and visualization."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._camera = CameraStream(config.camera)
        self._tracker = HandTracker(config.hand_tracking)
        self._steering_wheel = SteeringWheelOverlay(self._default_wheel_asset_path())
        self._steering_controller = SteeringController(config.steering.smoothing_alpha)
        self._steering_socket = SteeringSocketServer(
            host=config.socket.host,
            port=config.socket.port,
            send_rate_hz=config.socket.send_rate_hz,
        )
        self._steering_socket.start()
        self._fps_counter = FpsCounter()

    def run(self) -> None:
        """Start the realtime application loop."""
        cv2.namedWindow(self._config.ui.window_name, cv2.WINDOW_NORMAL)
        try:
            self._camera.open()

            while True:
                frame = self._camera.read()
                frame = cv2.flip(frame, 1)

                results = self._tracker.process(frame)
                observations = self._tracker.extract_observations(frame, results)
                raw_steering_angle_deg = self._calculate_current_steering_angle(observations)
                steering_state = self._steering_controller.process(raw_steering_angle_deg)
                self._steering_socket.send_steering(
                    self._normalize_steering_value(steering_state.smoothed_angle_deg)
                )

                self._steering_wheel.draw(frame, steering_state.smoothed_angle_deg)
                self._tracker.draw(frame, results)
                self._draw_hand_overlays(frame, observations, steering_state)
                draw_fps(frame, self._fps_counter.tick(), self._config.ui)

                cv2.imshow(self._config.ui.window_name, frame)
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC
                    break
                if key in (ord("c"), ord("C")) and steering_state.raw_angle_deg is not None:
                    self._steering_controller.calibrate(steering_state.raw_angle_deg)

        except CameraError as exc:
            print(f"[CameraError] {exc}")
        except Exception as exc:  # broad safety net for realtime app stability
            print(f"[RuntimeError] Unexpected error: {exc}")
        finally:
            self._shutdown()

    def _shutdown(self) -> None:
        """Release resources gracefully."""
        self._steering_socket.stop()
        self._camera.release()
        self._tracker.close()
        cv2.destroyAllWindows()

    def _normalize_steering_value(self, smoothed_angle_deg: float | None) -> float:
        """Map smoothed steering angle to [-1.0, +1.0] for game communication."""
        if smoothed_angle_deg is None:
            return 0.0
        max_angle = self._config.steering.max_steering_angle_deg
        if max_angle <= 0.0:
            return 0.0
        return max(-1.0, min(1.0, smoothed_angle_deg / max_angle))

    @staticmethod
    def _default_wheel_asset_path() -> Path:
        return Path(__file__).resolve().parent.parent / "assets" / "steering_wheel.png"

    def _draw_hand_overlays(
        self,
        frame: np.ndarray,
        observations: list[HandObservation],
        steering_state: SteeringState,
    ) -> None:
        """Draw hand overlays, steering state, and steering angle guides."""
        for observation in observations:
            center_x, center_y = observation.center
            cv2.circle(frame, (center_x, center_y), 8, (0, 255, 255), -1)
            cv2.putText(
                frame,
                observation.label,
                (center_x + 12, center_y - 12),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        if len(observations) == 2:
            left_center, right_center = self._resolve_left_right_centers(observations)
            distance_px = math.dist(left_center, right_center)

            cv2.line(frame, left_center, right_center, (0, 255, 0), 2)
            mid_x = int((left_center[0] + right_center[0]) / 2)
            mid_y = int((left_center[1] + right_center[1]) / 2)
            cv2.putText(
                frame,
                f"{distance_px:.1f}px",
                (mid_x + 10, mid_y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                frame,
                f"Steering Angle: {steering_state.calibrated_angle_deg:.1f}°",
                (20, 115),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                frame,
                f"Raw Angle: {steering_state.raw_angle_deg:.1f}°",
                (20, 150),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                frame,
                f"Smoothed Angle: {steering_state.smoothed_angle_deg:.1f}°",
                (20, 185),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                frame,
                "Steering Ready",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )
        else:
            cv2.putText(
                frame,
                "Waiting for two hands...",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )

        if self._steering_controller.should_show_calibration_message():
            cv2.putText(
                frame,
                "Calibration Complete",
                (20, 220),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )

        self._draw_steering_guides(frame, steering_state.calibrated_angle_deg)

    def _calculate_current_steering_angle(
        self, observations: list[HandObservation]
    ) -> float | None:
        """Return steering angle when two hands are visible; otherwise None."""
        if len(observations) != 2:
            return None
        left_center, right_center = self._resolve_left_right_centers(observations)
        return self._calculate_steering_angle_deg(left_center, right_center)

    def _resolve_left_right_centers(
        self, observations: list[HandObservation]
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        """Return centers in (LEFT, RIGHT) order for steering calculations."""
        labeled_centers = {obs.label: obs.center for obs in observations}
        if "LEFT" in labeled_centers and "RIGHT" in labeled_centers:
            return labeled_centers["LEFT"], labeled_centers["RIGHT"]

        sorted_by_x = sorted(observations, key=lambda obs: obs.center[0])
        return sorted_by_x[0].center, sorted_by_x[1].center

    def _calculate_steering_angle_deg(
        self, left_center: tuple[int, int], right_center: tuple[int, int]
    ) -> float:
        """
        Calculate steering angle from hand centers.

        0 deg: horizontal line
        Positive: clockwise tilt
        Negative: counter-clockwise tilt
        """
        dx = right_center[0] - left_center[0]
        dy = right_center[1] - left_center[1]
        return math.degrees(math.atan2(dy, dx))

    def _draw_steering_guides(self, frame: np.ndarray, steering_angle_deg: float | None) -> None:
        """Steering guide rendering is intentionally disabled."""
        _ = frame
        _ = steering_angle_deg


def main() -> None:
    app = VirtualSteeringWheelApp(AppConfig())
    app.run()


if __name__ == "__main__":
    main()
