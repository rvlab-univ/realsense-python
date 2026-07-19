import cv2
import numpy as np


def depth_colormap(depth: np.ndarray) -> np.ndarray:
    """16비트 깊이 배열을 확인용 BGR 컬러맵으로 변환한다."""
    return cv2.applyColorMap(cv2.convertScaleAbs(depth, alpha=0.03), cv2.COLORMAP_JET)


def side_by_side(rgb: np.ndarray, depth: np.ndarray) -> np.ndarray:
    """RGB와 깊이 컬러맵을 같은 높이로 맞춰 가로로 결합한다."""
    depth = depth_colormap(depth)
    if rgb.shape != depth.shape:
        rgb = cv2.resize(rgb, (depth.shape[1], depth.shape[0]), interpolation=cv2.INTER_AREA)
    return np.hstack((rgb, depth))
