"""Sample a captured RealSense video into COLMAP-ready JPEG frames."""

import argparse
import json
from pathlib import Path

import cv2


def sample_capture(capture_dir: Path, sample_fps: float) -> Path:
    """Write evenly spaced JPEG frames from ``video.mp4`` into ``images``."""
    if sample_fps <= 0:
        raise ValueError("sample_fps must be positive")

    # 파일 저장 경로 설정
    video_path = capture_dir / "video.mp4"
    output_dir = capture_dir / "images"
    if not video_path.is_file():
        raise FileNotFoundError(f"missing capture video: {video_path}")
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing sampled frames: {output_dir}")

    # 비디오 열기, 이미 저장된 mp4 파일을 열어서 프레임을 읽어오는 작업
    video = cv2.VideoCapture(str(video_path))
    if not video.isOpened():
        raise RuntimeError(f"cannot open video: {video_path}")

    try:
        # 대충 프레임 수와 FPS를 가져옴
        source_fps = float(video.get(cv2.CAP_PROP_FPS))
        source_frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        if source_fps <= 0:
            raise RuntimeError(f"invalid source FPS: {source_fps}")

        output_dir.mkdir()
        next_sample_frame = 0.0
        frame_index = 0
        sampled_frame_count = 0
        interval = source_fps / sample_fps

        # 이제 비디오를 읽으면서 sample_fps에 맞춰서 프레임을 저장
        while True:
            ok, frame = video.read()
            if not ok:
                break
            if frame_index + 1e-9 >= next_sample_frame:
                timestamp = frame_index / source_fps
                output_path = output_dir / f"frame_{frame_index:06d}_{timestamp:010.3f}s.jpg"

                if not cv2.imwrite(str(output_path), frame):
                    raise RuntimeError(f"failed to write sampled frame: {output_path}")
                
                sampled_frame_count += 1
                next_sample_frame += interval
            frame_index += 1
    finally:
        video.release()

    # 마지막에는 메타데이터까지 같이 저장하면서~
    with (capture_dir / "sampling.json").open("w") as file:
        json.dump(
            {
                "source_fps": source_fps,
                "sample_fps": sample_fps,
                "source_frame_count": source_frame_count,
                "sampled_frame_count": sampled_frame_count,
            },
            file,
            indent=2,
        )
    return output_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--fps", type=float, default=5, help="Output JPEG sampling rate")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    images = sample_capture(args.capture_dir, args.fps)
    # (realsense-python) ahris@ahris:~/workspace/realsense-python$ uv run src/sampler.py --capture-dir outputs/captures/data01 --fps 5
    print(f"Sampled frames written to: {images}")
