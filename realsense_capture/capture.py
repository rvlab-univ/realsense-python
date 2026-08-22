import json
from os import PathLike
from pathlib import Path
from typing import Protocol

import cv2
import numpy as np

__all__ = [
    "VideoRecorder",
    "capture_video",
    "save_capture_metadata",
    "save_image",
    "save_intrinsics",
]


def save_image(image: np.ndarray, path: str | PathLike[str]) -> bool:
    """BGR 이미지를 지정한 경로에 저장한다."""
    return cv2.imwrite(str(path), image)


def save_intrinsics(intrinsics: dict[str, object], path: str | PathLike[str]) -> None:
    """카메라 내부 파라미터를 JSON 파일로 저장한다."""
    with Path(path).open("w") as file:
        json.dump(intrinsics, file)


def save_capture_metadata(metadata: dict[str, object], path: str | PathLike[str]) -> None:
    """캡처 재현에 필요한 설정을 JSON 파일로 저장한다."""
    with Path(path).open("w") as file:
        json.dump(metadata, file, indent=2)

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
