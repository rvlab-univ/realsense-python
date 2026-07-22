import os
import cv2

from src.camera import start
from src.processing import side_by_side

def main():
    """RGB와 Depth 스트림을 나란히 보여 주는 실행 예제다."""

    camera = start("rgb", "depth")

    try:
        while True:
            frames = camera.read()
            image = side_by_side(frames.rgb, frames.depth) # 후처리, 이미지를 한 화면에 띄울 수 있도록 만들어줌

            cv2.imshow("RealSense", image)
            if cv2.waitKey(1) in (ord("q"), 27):
                break
    finally:
        if image is not None:
            save_path = "outputs/images"
            os.makedirs(save_path, exist_ok=True)
            full_path = os.path.join(save_path, "image.png")
            
            cv2.imwrite(full_path, image)
            print(f"image saved: {full_path}")

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
