import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parents[1]))

from src import visualization


class CV2:
    def __init__(self, key):
        self.key = key
        self.image = None

    def imshow(self, title, image):
        self.title = title
        self.image = image

    def waitKey(self, delay):
        return self.key


def test_show_returns_false_for_quit_key(monkeypatch):
    cv2 = CV2(ord("q"))
    monkeypatch.setattr(visualization, "cv2", cv2)

    keep_open = visualization.show(np.zeros((2, 2, 3), dtype=np.uint8))

    assert keep_open is False
    assert cv2.title == "RealSense"


def test_show_returns_true_for_other_key(monkeypatch):
    monkeypatch.setattr(visualization, "cv2", CV2(-1))

    assert visualization.show(np.zeros((2, 2, 3), dtype=np.uint8)) is True
