import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parents[1]))

from src import capture


class Writer:
    def __init__(self):
        self.frames = []
        self.released = False

    def write(self, frame):
        self.frames.append(frame)

    def release(self):
        self.released = True


class CV2:
    def __init__(self):
        self.saved_images = []
        self.writer_args = None
        self.writer = Writer()

    def imwrite(self, path, image):
        self.saved_images.append((path, image))
        return True

    def VideoWriter_fourcc(self, *codec):
        return codec

    def VideoWriter(self, path, fourcc, fps, size):
        self.writer_args = (path, fourcc, fps, size)
        return self.writer


def test_capture_image_writes_one_frame(monkeypatch):
    cv2 = CV2()
    image = np.zeros((2, 3, 3), dtype=np.uint8)
    monkeypatch.setattr(capture, "cv2", cv2, raising=False)

    assert capture.capture_image(image, "frame.png") is True
    assert cv2.saved_images == [("frame.png", image)]


def test_capture_video_writes_frames_and_releases_writer(monkeypatch):
    cv2 = CV2()
    image = np.ones((2, 3, 3), dtype=np.uint8)
    monkeypatch.setattr(capture, "cv2", cv2)

    with capture.capture_video("capture.mp4") as video:
        video.write(image)

    assert cv2.writer_args == ("capture.mp4", ("m", "p", "4", "v"), 30, (3, 2))
    assert cv2.writer.frames == [image]
    assert cv2.writer.released is True
