import cv2
import numpy as np


def show(image: np.ndarray, title: str = "RealSense") -> bool:
    """이미지를 표시하고 계속 실행할지 반환한다."""
    cv2.imshow(title, image)
    return cv2.waitKey(1) not in (ord("q"), 27)
