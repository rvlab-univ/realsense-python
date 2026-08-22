from dataclasses import dataclass

import numpy as np
import pyrealsense2 as rs

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

    @property
    def accel(self) -> np.ndarray | None:
        """가속도계 측정값(m/s^2, xyz)을 반환한다. 이번 프레임셋에 없으면 None."""
        return self._motion_data(rs.stream.accel)

    @property
    def gyro(self) -> np.ndarray | None:
        """자이로 각속도(rad/s, xyz)를 반환한다. 이번 프레임셋에 없으면 None."""
        return self._motion_data(rs.stream.gyro)

    @property
    def timestamp_ms(self) -> float:
        """프레임셋의 타임스탬프(ms)를 반환한다. 프레임 간 dt 계산에 쓴다."""
        return self.raw.get_timestamp()

    def _motion_data(self, stream_type: rs.stream) -> np.ndarray | None:
        frame = self.raw.first_or_default(stream_type)
        if not frame:
            return None
        data = frame.as_motion_frame().get_motion_data()
        return np.array([data.x, data.y, data.z])


class Camera:
    """RealSense 파이프라인의 프레임 수신과 종료를 담당한다."""

    def __init__(self, config: rs.config):
        """전달받은 스트림 설정으로 카메라 객체를 만든다."""
        self.pipeline = rs.pipeline()
        self.config = config

    def read(self) -> Frames:
        """동기화된 프레임셋 하나를 수신한다."""
        return Frames(self.pipeline.wait_for_frames())

    @property
    def intrinsics(self) -> dict[str, object]:
        """현재 컬러 스트림의 내부 파라미터를 딕셔너리로 반환한다."""
        profile = self.pipeline.get_active_profile()
        stream = profile.get_stream(rs.stream.color).as_video_stream_profile()
        intrinsics = stream.get_intrinsics()
        return {
            "width": intrinsics.width,
            "height": intrinsics.height,
            "fx": intrinsics.fx,
            "fy": intrinsics.fy,
            "ppx": intrinsics.ppx,
            "ppy": intrinsics.ppy,
            "model": getattr(intrinsics.model, "name", str(intrinsics.model)),
            "coeffs": list(intrinsics.coeffs),
        }

    def imu_extrinsics(self, to_stream: rs.stream = rs.stream.color) -> tuple[np.ndarray, np.ndarray]:
        """자이로 좌표계 -> to_stream 좌표계로 변환하는 (회전 3x3, 이동 3) 튜플을 반환한다."""
        profile = self.pipeline.get_active_profile()
        gyro_stream = profile.get_stream(rs.stream.gyro)
        target_stream = profile.get_stream(to_stream)
        extrinsics = gyro_stream.get_extrinsics_to(target_stream)
        rotation = np.array(extrinsics.rotation).reshape(3, 3).T  # librealsense는 column-major로 반환
        translation = np.array(extrinsics.translation)
        return rotation, translation

    def stop(self) -> None:
        """실행 중인 RealSense 파이프라인을 종료한다."""
        self.pipeline.stop()


def list_devices() -> list[dict[str, str]]:
    """연결된 RealSense 장치 목록을 이름과 시리얼 번호로 반환한다."""
    devices = []
    for device in rs.context().query_devices():
        devices.append(
            {
                "name": device.get_info(rs.camera_info.name),
                "serial_number": device.get_info(rs.camera_info.serial_number),
                "firmware_version": device.get_info(rs.camera_info.firmware_version),
            }
        )
    return devices


def start(*streams: str, width=640, height=480, fps=30) -> Camera:
    """요청한 스트림을 활성화하고 실행 중인 카메라 객체를 반환한다."""
    config = rs.config()
    if "rgb" in streams:
        config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
    if "depth" in streams:
        config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
    if "ir" in streams or "stereo" in streams:
        config.enable_stream(rs.stream.infrared, 1, width, height, rs.format.y8, fps)
        config.enable_stream(rs.stream.infrared, 2, width, height, rs.format.y8, fps)
    # rgb/depth 같은 비디오 스트림과 함께 열 때는 fps를 명시하지 않으면 resolve가 실패한다.
    if "accel" in streams or "imu" in streams:
        config.enable_stream(rs.stream.accel, rs.format.motion_xyz32f, 200)
    if "gyro" in streams or "imu" in streams:
        config.enable_stream(rs.stream.gyro, rs.format.motion_xyz32f, 200)

    camera = Camera(config)
    camera.pipeline.start(config)
    return camera
