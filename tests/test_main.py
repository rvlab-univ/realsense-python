import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))
import main as example


class Camera:
    def __init__(self, frames):
        self.frames = frames
        self.stopped = False

    def read(self):
        return self.frames

    def stop(self):
        self.stopped = True


class CV2:
    def __init__(self):
        self.images = []
        self.wait_delays = []
        self.destroyed = False

    def imshow(self, title, image):
        self.images.append((title, image))

    def waitKey(self, delay):
        self.wait_delays.append(delay)
        return ord("q")

    def destroyAllWindows(self):
        self.destroyed = True


def test_main_displays_combined_rgb_and_depth_frame(monkeypatch):
    rgb = object()
    depth = object()
    combined = object()
    camera = Camera(SimpleNamespace(rgb=rgb, depth=depth))
    cv2 = CV2()
    received_images = []

    monkeypatch.setattr(example, "start", lambda *streams: camera)
    monkeypatch.setattr(
        example,
        "side_by_side",
        lambda received_rgb, received_depth: received_images.append(
            (received_rgb, received_depth)
        )
        or combined,
    )
    monkeypatch.setattr(example, "cv2", cv2)

    example.main()

    assert received_images == [(rgb, depth)]
    assert cv2.images == [("RealSense", combined)]
    assert cv2.wait_delays == [1]


def test_main_releases_camera_and_windows_when_processing_fails(monkeypatch):
    camera = Camera(SimpleNamespace(rgb=object(), depth=object()))
    cv2 = CV2()

    monkeypatch.setattr(example, "start", lambda *streams: camera)
    monkeypatch.setattr(
        example,
        "side_by_side",
        lambda rgb, depth: (_ for _ in ()).throw(RuntimeError("processing failed")),
    )
    monkeypatch.setattr(example, "cv2", cv2)

    with pytest.raises(RuntimeError, match="processing failed"):
        example.main()

    assert camera.stopped is True
    assert cv2.destroyed is True
