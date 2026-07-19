import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parents[1]))

from src.processing import depth_colormap, side_by_side


def test_depth_colormap_returns_bgr_image():
    depth = np.array([[0, 1000]], dtype=np.uint16)

    image = depth_colormap(depth)

    assert image.shape == (1, 2, 3)
    assert image.dtype == np.uint8


def test_side_by_side_resizes_rgb_to_depth_size():
    rgb = np.zeros((2, 4, 3), dtype=np.uint8)
    depth = np.zeros((4, 2), dtype=np.uint16)

    image = side_by_side(rgb, depth)

    assert image.shape == (4, 4, 3)
