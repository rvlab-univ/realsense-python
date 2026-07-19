from dataclasses import dataclass

import numpy as np
import pyrealsense2 as rs

WIDTH, HEIGHT, FPS = 640, 480, 30

@dataclass
class Frames:
    """한 번 수신한 RealSense 프레임에서 필요한 배열 데이터를 꺼낸다."""

    raw: rs.composite_frame

    @property
    def rgb(self) -> np.ndarray:
        """BGR 형식의 RGB 카메라 프레임을 반환한다."""
        return np.asanyarray(self.raw.get_color_frame().get_data())

    @property
    def depth(self) -> np.ndarray:
        """16비트 깊이 프레임을 반환한다."""
        return np.asanyarray(self.raw.get_depth_frame().get_data())

    def ir(self, index: int) -> np.ndarray:
        """지정한 번호(1 또는 2)의 IR 프레임을 반환한다."""
        return np.asanyarray(self.raw.get_infrared_frame(index).get_data())

    @property
    def stereo(self) -> tuple[np.ndarray, np.ndarray]:
        """왼쪽과 오른쪽 IR 프레임을 튜플로 반환한다."""
        return self.ir(1), self.ir(2)


class Camera:
    """RealSense 파이프라인의 프레임 수신과 종료를 담당한다."""

    def __init__(self, config: rs.config):
        """전달받은 스트림 설정으로 카메라 객체를 만든다."""
        self.pipeline = rs.pipeline()
        self.config = config

    def read(self) -> Frames:
        """동기화된 프레임셋 하나를 수신한다."""
        return Frames(self.pipeline.wait_for_frames())

    def stop(self) -> None:
        """실행 중인 RealSense 파이프라인을 종료한다."""
        self.pipeline.stop()


def start(*streams: str) -> Camera:
    """요청한 스트림을 활성화하고 실행 중인 카메라 객체를 반환한다."""
    config = rs.config()
    if "rgb" in streams:
        config.enable_stream(rs.stream.color, WIDTH, HEIGHT, rs.format.bgr8, FPS)
    if "depth" in streams:
        config.enable_stream(rs.stream.depth, WIDTH, HEIGHT, rs.format.z16, FPS)
    if "ir" in streams or "stereo" in streams:
        config.enable_stream(rs.stream.infrared, 1, WIDTH, HEIGHT, rs.format.y8, FPS)
        config.enable_stream(rs.stream.infrared, 2, WIDTH, HEIGHT, rs.format.y8, FPS)

    camera = Camera(config)
    camera.pipeline.start(config)
    return camera
