# Image Capture Metadata Design

## Goal

Save an original RealSense colour frame and the colour camera intrinsics needed
to interpret its pixels later. Keep camera access, file writing, and keyboard
interaction separate so each part stays easy to read.

## Design

- `src/camera.py` exposes `Camera.intrinsics`. It reads the active colour
  stream profile and returns a plain dictionary containing image size, focal
  lengths, principal point, distortion model, and distortion coefficients.
- `src/capture.py` provides two small file-writing functions:
  `save_image(image, path)` writes the caller-provided BGR image with OpenCV;
  `save_intrinsics(intrinsics, path)` writes the caller-provided dictionary as
  JSON. Neither function imports or knows about RealSense.
- `main.py` remains an example program. It displays the RGB/depth preview and
  saves `frames.rgb` plus `camera.intrinsics` when `s` is pressed. The preview
  image is never used as capture data.
- Video capture stays in its separate example file. It can call the same
  intrinsic-saving function once beside a video, without adding keyboard or
  video logic to `src/capture.py`.

## Data Format

The image is a lossless PNG containing the original BGR `uint8` colour frame.
The adjacent JSON contains:

```json
{
  "width": 640,
  "height": 480,
  "fx": 0.0,
  "fy": 0.0,
  "ppx": 0.0,
  "ppy": 0.0,
  "model": "...",
  "coeffs": [0.0, 0.0, 0.0, 0.0, 0.0]
}
```

## Non-goals

- Do not save depth images, depth scale, stream extrinsics, timestamps, or
  frame sequences in this change.
- Do not add a capture UI abstraction or detailed error recovery.

## Verification

Add focused tests for intrinsic conversion and the JSON writer, then run the
`realsense-python` test suite.
