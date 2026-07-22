import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parents[1]))

from src import camera


class Frame:
    def __init__(self, image):
        self.image = image

    def get_data(self):
        return self.image


class RawFrames:
    def get_color_frame(self):
        return Frame(np.full((2, 3, 3), 10, dtype=np.uint8))

    def get_depth_frame(self):
        return Frame(np.full((2, 3), 1000, dtype=np.uint16))

    def get_infrared_frame(self, index):
        return Frame(np.full((2, 3), index, dtype=np.uint8))


class Pipeline:
    def __init__(self):
        self.started = None
        self.stopped = False

    def start(self, config):
        self.started = config

    def wait_for_frames(self):
        return RawFrames()

    def get_active_profile(self):
        return ActiveProfile()

    def stop(self):
        self.stopped = True


class Config:
    def __init__(self):
        self.enabled = []

    def enable_stream(self, *stream):
        self.enabled.append(stream)


class Intrinsics:
    width = 640
    height = 480
    fx = 600.0
    fy = 601.0
    ppx = 320.0
    ppy = 240.0
    model = "brown_conrady"
    coeffs = (1.0, 2.0, 3.0, 4.0, 5.0)


class VideoStreamProfile:
    def get_intrinsics(self):
        return Intrinsics()

    def as_video_stream_profile(self):
        return self


class ActiveProfile:
    def get_stream(self, stream):
        assert stream == "color"
        return VideoStreamProfile()


class RealSense:
    pipeline = Pipeline
    config = Config

    class stream:
        color = "color"
        depth = "depth"
        infrared = "infrared"

    class format:
        bgr8 = "bgr8"
        z16 = "z16"
        y8 = "y8"


def test_start_enables_requested_streams(monkeypatch):
    monkeypatch.setattr(camera, "rs", RealSense)

    device = camera.start("rgb", "depth", "ir")

    assert device.config.enabled == [
        ("color", 640, 480, "bgr8", 30),
        ("depth", 640, 480, "z16", 30),
        ("infrared", 1, 640, 480, "y8", 30),
        ("infrared", 2, 640, 480, "y8", 30),
    ]


def test_read_exposes_requested_data_from_one_frameset(monkeypatch):
    monkeypatch.setattr(camera, "rs", RealSense)
    device = camera.start("rgb", "depth", "stereo")

    frames = device.read()

    assert frames.rgb.shape == (2, 3, 3)
    assert frames.depth.dtype == np.uint16
    assert np.array_equal(frames.ir(2), np.full((2, 3), 2, dtype=np.uint8))
    left, right = frames.stereo
    assert np.array_equal(left, np.full((2, 3), 1, dtype=np.uint8))
    assert np.array_equal(right, np.full((2, 3), 2, dtype=np.uint8))


def test_intrinsics_returns_color_stream_calibration(monkeypatch):
    monkeypatch.setattr(camera, "rs", RealSense)
    device = camera.start("rgb")

    assert device.intrinsics == {
        "width": 640,
        "height": 480,
        "fx": 600.0,
        "fy": 601.0,
        "ppx": 320.0,
        "ppy": 240.0,
        "model": "brown_conrady",
        "coeffs": [1.0, 2.0, 3.0, 4.0, 5.0],
    }
