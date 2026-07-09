"""Application configuration values for the virtual steering wheel project."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CameraConfig:
    """Camera-related runtime settings."""

    device_index: int = 0
    width: int = 1280
    height: int = 720


@dataclass(frozen=True, slots=True)
class HandTrackingConfig:
    """MediaPipe hand tracking parameters."""

    max_num_hands: int = 2
    min_detection_confidence: float = 0.7
    min_tracking_confidence: float = 0.6


@dataclass(frozen=True, slots=True)
class SteeringConfig:
    """Steering calibration and smoothing settings."""

    smoothing_alpha: float = 0.2
    max_steering_angle_deg: float = 45.0


@dataclass(frozen=True, slots=True)
class SocketConfig:
    """Socket settings for game communication."""

    host: str = "127.0.0.1"
    port: int = 5555
    send_rate_hz: int = 60


@dataclass(frozen=True, slots=True)
class UiConfig:
    """UI and visualization settings."""

    window_name: str = "Virtual Steering Wheel - Hand Tracking"
    fps_position: tuple[int, int] = (20, 40)
    font_scale: float = 1.0
    font_thickness: int = 2
    font_color_bgr: tuple[int, int, int] = (60, 255, 60)


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Top-level application configuration object."""

    camera: CameraConfig = CameraConfig()
    hand_tracking: HandTrackingConfig = HandTrackingConfig()
    steering: SteeringConfig = SteeringConfig()
    socket: SocketConfig = SocketConfig()
    ui: UiConfig = UiConfig()
