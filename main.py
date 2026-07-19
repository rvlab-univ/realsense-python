import cv2

from src.camera import start
from src.processing import side_by_side
from src.visualization import show

def main():
    """RGB와 Depth 스트림을 나란히 보여 주는 실행 예제다."""
    camera = start("rgb", "depth")
    while show(side_by_side((frames := camera.read()).rgb, frames.depth)):
        pass
    camera.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
