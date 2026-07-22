import cv2
from pathlib import Path

from src.camera import start
from src.capture import save_image, save_intrinsics
from src.processing import side_by_side


def main():
    """RGB와 Depth 스트림을 나란히 보여 주는 실행 예제다."""

    camera = start("rgb", "depth")

    try:
        while True:
            frames = camera.read()
            image = side_by_side(frames.rgb, frames.depth) # 후처리, 이미지를 한 화면에 띄울 수 있도록 만들어줌

            cv2.imshow("RealSense", image)
            key = cv2.waitKey(1)
            if key == ord("s"):
                output_path = Path("outputs/images")
                output_path.mkdir(parents=True, exist_ok=True)
                save_image(frames.rgb, output_path / "image.png")
                save_intrinsics(camera.intrinsics, output_path / "intrinsics.json")
                print("image saved: outputs/images/image.png")
            if key in (ord("q"), 27):
                break
    finally:
        camera.stop()
        cv2.destroyAllWindows()

    # IR만 확인하려면 아래걸로 대체
    # camera = start("ir")
    # try:
    #     while True:
    #         frames = camera.read()
    #         cv2.imshow("Infrared 1", frames.ir(1))
    #         if cv2.waitKey(1) in (ord("q"), 27):
    #             break
    # finally:
    #     camera.stop()
    #     cv2.destroyAllWindows()



if __name__ == "__main__":
    main()
