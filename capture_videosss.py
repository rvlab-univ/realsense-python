"""Record a RealSense RGB capture for later 3DGS/COLMAP preprocessing."""

import argparse
from datetime import datetime, timezone
from pathlib import Path

import cv2

from src.camera import start
from src.capture import capture_video, save_capture_metadata, save_intrinsics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Scene name, e.g. desk_01")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/captures"))
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--duration", type=float, help="Optional maximum recording duration in seconds")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    capture_dir = args.output_dir / args.name
    if capture_dir.exists():
        raise FileExistsError(f"capture directory already exists: {capture_dir}")
    capture_dir.mkdir(parents=True)

    video_path = capture_dir / "video.mp4"
    camera = start("rgb", width=args.width, height=args.height, fps=args.fps)
    started_at = datetime.now(timezone.utc)
    frame_count = 0

    try:
        with capture_video(video_path, args.fps) as video:
            while True:
                frames = camera.read()
                video.write(frames.rgb)
                frame_count += 1
                cv2.imshow("RealSense (q or Esc to stop)", frames.rgb)
                elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
                if cv2.waitKey(1) in (ord("q"), 27) or (
                    args.duration is not None and elapsed >= args.duration
                ):
                    break
    finally:
        save_intrinsics(camera.intrinsics, capture_dir / "intrinsics.json")
        save_capture_metadata(
            {
                "video": video_path.name,
                "color_fps": args.fps,
                "requested_width": args.width,
                "requested_height": args.height,
                "started_at": started_at.isoformat(),
                "recorded_frame_count": frame_count,
            },
            capture_dir / "capture.json",
        )
        camera.stop()
        cv2.destroyAllWindows()

    print(f"Capture saved to: {capture_dir}")


if __name__ == "__main__":
    main()
