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

    def stop(self):
        self.stopped = True


class Config:
    def __init__(self):
        self.enabled = []

    def enable_stream(self, *stream):
        self.enabled.append(stream)


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
