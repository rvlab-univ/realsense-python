import json
import sys
from pathlib import Path

import numpy as np


sys.path.insert(0, str(Path(__file__).parents[1]))

try:
    from postprocessing import sampler
except ModuleNotFoundError:
    sampler = None


class FakeVideo:
    def __init__(self):
        self.index = 0

    def isOpened(self):
        return True

    def get(self, property_id):
        if property_id == FakeCV2.CAP_PROP_FPS:
            return 10.0
        if property_id == FakeCV2.CAP_PROP_FRAME_COUNT:
            return 20.0
        return 0.0

    def read(self):
        if self.index == 20:
            return False, None
        frame = np.full((2, 3, 3), self.index, dtype=np.uint8)
        self.index += 1
        return True, frame

    def release(self):
        pass


class FakeCV2:
    CAP_PROP_FPS = 5
    CAP_PROP_FRAME_COUNT = 7

    def VideoCapture(self, path):
        return FakeVideo()

    def imwrite(self, path, frame):
        Path(path).write_bytes(frame.tobytes())
        return True


def test_sample_capture_writes_evenly_spaced_jpegs_and_sampling_metadata(
    monkeypatch, tmp_path
):
    assert sampler is not None, "postprocessing.sampler module is missing"
    capture_dir = tmp_path / "scene"
    capture_dir.mkdir()
    (capture_dir / "video.mp4").write_bytes(b"video")
    monkeypatch.setattr(sampler, "cv2", FakeCV2())

    output_dir = sampler.sample_capture(capture_dir, sample_fps=2)

    assert [path.name for path in sorted(output_dir.glob("*.jpg"))] == [
        "frame_000000_000000.000s.jpg",
        "frame_000005_000000.500s.jpg",
        "frame_000010_000001.000s.jpg",
        "frame_000015_000001.500s.jpg",
    ]
    assert json.loads((capture_dir / "sampling.json").read_text()) == {
        "source_fps": 10.0,
        "sample_fps": 2,
        "source_frame_count": 20,
        "sampled_frame_count": 4,
    }
