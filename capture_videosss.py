
from pathlib import Path

import cv2
import numpy as np

def main() -> None:
    """위에 있는 함수들로 캡쳐하는 방법 예제입니다."""
    from src.camera import start
    from src.processing import side_by_side
    from src.capture import capture_video

    output_path = Path("outputs/video.mp4") # 저장경로 명시
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 카메라 캡쳐 실행
    camera = start("rgb")

    try:
        # 비디오 캡쳐 시하는 with 구문, 프레임은 30fps가 기본, 원하면 명시
        with capture_video(output_path, 5) as video:
            while True:
                frames = camera.read() # 데이터 받아와서
                video.write(frames.rgb)

                cv2.imshow("RealSense", frames.rgb)
                if cv2.waitKey(1) in (ord("q"), 27):
                    break
    finally:
        camera.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
