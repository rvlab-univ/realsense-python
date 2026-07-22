import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))
import main as example


class Camera:
    def __init__(self, frames, intrinsics=None):
        self.frames = frames
        self.intrinsics = intrinsics or {"fx": 600.0}
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

    monkeypatch.setattr(example, "start", lambda *streams, **settings: camera)
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


def test_main_starts_camera_with_configured_capture_dimensions(monkeypatch):
    camera = Camera(SimpleNamespace(rgb=object(), depth=object()))
    cv2 = CV2()
    start_calls = []

    monkeypatch.setattr(
        example,
        "start",
        lambda *streams, **settings: start_calls.append((streams, settings)) or camera,
    )
    monkeypatch.setattr(example, "side_by_side", lambda rgb, depth: object())
    monkeypatch.setattr(example, "cv2", cv2)

    example.main()

    assert start_calls == [
        (
            ("rgb", "depth"),
            {
                "width": example.CAPTURE_WIDTH,
                "height": example.CAPTURE_HEIGHT,
                "fps": example.CAPTURE_FPS,
            },
        )
    ]


def test_main_releases_camera_and_windows_when_processing_fails(monkeypatch):
    camera = Camera(SimpleNamespace(rgb=object(), depth=object()))
    cv2 = CV2()

    monkeypatch.setattr(example, "start", lambda *streams, **settings: camera)
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


def test_main_saves_raw_bgr_image_and_intrinsics_when_s_is_pressed(monkeypatch):
    rgb = object()
    camera = Camera(SimpleNamespace(rgb=rgb, depth=object()), {"fx": 600.0})
    cv2 = CV2()
    keys = iter((ord("s"), ord("q")))
    saved_images = []
    saved_intrinsics = []

    monkeypatch.setattr(example, "start", lambda *streams, **settings: camera)
    monkeypatch.setattr(example, "side_by_side", lambda rgb, depth: object())
    monkeypatch.setattr(example, "cv2", cv2)
    monkeypatch.setattr(cv2, "waitKey", lambda delay: next(keys))
    monkeypatch.setattr(
        example, "save_image", lambda image, path: saved_images.append((image, path))
    )
    monkeypatch.setattr(
        example,
        "save_intrinsics",
        lambda intrinsics, path: saved_intrinsics.append((intrinsics, path)),
    )

    example.main()

    assert saved_images == [(rgb, Path("outputs/images/image.png"))]
    assert saved_intrinsics == [
        ({"fx": 600.0}, Path("outputs/images/intrinsics.json"))
    ]
