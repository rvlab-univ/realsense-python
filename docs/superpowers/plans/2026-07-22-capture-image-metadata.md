# Image Capture Metadata Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Save a BGR RealSense image and its colour-camera intrinsics without coupling file storage to the camera or UI.

**Architecture:** `Camera` exposes a plain intrinsic dictionary derived from the active colour stream. `capture.py` accepts caller-provided data and writes image/JSON files. `main.py` combines them when the user presses `s`.

**Tech Stack:** Python 3.12, pyrealsense2, OpenCV, JSON, pytest.

## Global Constraints

- Keep camera access, file writing, and keyboard handling separate.
- Store the source BGR `uint8` image, not the display composite.
- Keep exception handling and validation minimal.
- Do not add depth, extrinsic, timestamp, or sequence support.

---

### Task 1: Expose colour intrinsics from `Camera`

**Files:**
- Modify: `src/camera.py`
- Test: `tests/test_camera.py`

**Interfaces:**
- Produces: `Camera.intrinsics -> dict[str, object]` with `width`, `height`, `fx`, `fy`, `ppx`, `ppy`, `model`, and `coeffs`.

- [ ] **Step 1: Write the failing test**

```python
def test_intrinsics_returns_color_stream_calibration(monkeypatch):
    monkeypatch.setattr(camera, "rs", RealSense)
    device = camera.start("rgb")

    assert device.intrinsics == {
        "width": 640, "height": 480, "fx": 600.0, "fy": 601.0,
        "ppx": 320.0, "ppy": 240.0, "model": "brown_conrady",
        "coeffs": [1.0, 2.0, 3.0, 4.0, 5.0],
    }
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_camera.py::test_intrinsics_returns_color_stream_calibration -v`
Expected: FAIL because `Camera` has no `intrinsics` property.

- [ ] **Step 3: Write minimal implementation**

```python
@property
def intrinsics(self) -> dict[str, object]:
    profile = self.pipeline.get_active_profile()
    intrinsics = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
    return {"width": intrinsics.width, "height": intrinsics.height,
            "fx": intrinsics.fx, "fy": intrinsics.fy,
            "ppx": intrinsics.ppx, "ppy": intrinsics.ppy,
            "model": str(intrinsics.model), "coeffs": list(intrinsics.coeffs)}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_camera.py -v`
Expected: PASS.

### Task 2: Add independent image and metadata writers

**Files:**
- Modify: `src/capture.py`
- Test: `tests/test_capture.py`

**Interfaces:**
- Produces: `save_image(image: np.ndarray, path: str | PathLike[str]) -> bool`
- Produces: `save_intrinsics(intrinsics: dict[str, object], path: str | PathLike[str]) -> None`

- [ ] **Step 1: Write failing tests**

```python
def test_save_image_writes_caller_provided_bgr_frame(monkeypatch):
    cv2 = CV2()
    monkeypatch.setattr(capture, "cv2", cv2)
    image = np.zeros((2, 3, 3), dtype=np.uint8)
    assert capture.save_image(image, "frame.png") is True
    assert cv2.saved_images == [("frame.png", image)]

def test_save_intrinsics_writes_json(tmp_path):
    path = tmp_path / "intrinsics.json"
    capture.save_intrinsics({"fx": 600.0}, path)
    assert path.read_text() == '{"fx": 600.0}'
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_capture.py -v`
Expected: FAIL because the two functions are undefined.

- [ ] **Step 3: Write minimal implementation**

```python
def save_image(image: np.ndarray, path: str | PathLike[str]) -> bool:
    return cv2.imwrite(str(path), image)

def save_intrinsics(intrinsics: dict[str, object], path: str | PathLike[str]) -> None:
    with Path(path).open("w") as file:
        json.dump(intrinsics, file)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_capture.py -v`
Expected: PASS.

### Task 3: Save a capture from the interactive example

**Files:**
- Modify: `main.py`
- Test: `tests/test_main.py`

**Interfaces:**
- Consumes: `capture.save_image`, `capture.save_intrinsics`, `Camera.intrinsics`.
- Produces: `s` key saves `outputs/images/image.png` and `outputs/images/intrinsics.json`.

- [ ] **Step 1: Write the failing test**

```python
def test_main_saves_raw_bgr_image_and_intrinsics(monkeypatch):
    # configure a one-frame camera and cv2.waitKey() returning ord("s"), then ord("q")
    main.main()
    assert saved_image == camera.frames.rgb
    assert saved_intrinsics == camera.intrinsics
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_main.py::test_main_saves_raw_bgr_image_and_intrinsics -v`
Expected: FAIL because `s` has no save behaviour.

- [ ] **Step 3: Write minimal implementation**

```python
if key == ord("s"):
    output_path = Path("outputs/images")
    output_path.mkdir(parents=True, exist_ok=True)
    save_image(frames.rgb, output_path / "image.png")
    save_intrinsics(camera.intrinsics, output_path / "intrinsics.json")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_main.py -v`
Expected: PASS.

- [ ] **Step 5: Run the suite**

Run: `uv run pytest -v`
Expected: PASS.
