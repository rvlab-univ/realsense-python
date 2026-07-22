from os import PathLike
from pathlib import Path
from typing import Protocol

import cv2
import numpy as np

__all__ = ["VideoRecorder", "capture_video"]

class VideoWriter(Protocol):
    def write(self, image: np.ndarray) -> None: ...

    def release(self) -> None: ...


class VideoRecorder:
    """Write caller-provided frames and release the video file on exit."""

    def __init__(self, output_path: str | PathLike[str], fps: int = 30):
        self.output_path = str(output_path)
        self.fps = fps
        self._writer: VideoWriter | None = None

    def __enter__(self) -> "VideoRecorder":
        return self

    def __exit__(self, *_: object) -> None:
        if self._writer is not None:
            self._writer.release()

    def write(self, image: np.ndarray) -> None:
        if self._writer is None:
            height, width = image.shape[:2]
            self._writer = cv2.VideoWriter(
                self.output_path,
                cv2.VideoWriter_fourcc(*"mp4v"),
                self.fps,
                (width, height),
            )
        self._writer.write(image)

def capture_video(
    output_path: str | PathLike[str], fps: int = 30
) -> VideoRecorder:
    """Create a context manager that records frames supplied by the caller."""
    return VideoRecorder(output_path, fps)


def main() -> None:
    """위에 있는 함수들로 캡쳐하는 방법 예제입니다."""
    from .camera import start
    from .processing import side_by_side

    output_path = Path("outputs/video.mp4") # 저장경로 명시
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 카메라 캡쳐 실행
    camera = start("rgb", "depth")

    try:
        # 비디오 캡쳐 시하는 with 구문, 프레임은 30fps가 기본, 원하면 명시
        with capture_video(output_path) as video:
            while True:
                frames = camera.read() # 데이터 받아와서
                image = side_by_side(frames.rgb, frames.depth)
                video.write(image)

                cv2.imshow("RealSense", image)
                if cv2.waitKey(1) in (ord("q"), 27):
                    break
    finally:
        camera.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
