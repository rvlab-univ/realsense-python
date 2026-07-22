# Inline OpenCV Main Example Design

## Goal

Make `main.py` a self-contained RealSense usage example. Readers should be
able to see how a frame is received, accessed, processed, displayed, and
cleaned up without following a visualization wrapper.

## Scope

- Remove `src/visualization.py` and its dedicated tests.
- In `main.py`, receive a `Frames` object with `camera.read()`, combine its
  `rgb` and `depth` arrays with `side_by_side()`, and display the result with
  OpenCV directly.
- End the loop when the user presses `q` or Escape.
- Use `try`/`finally` so `camera.stop()` and `cv2.destroyAllWindows()` run
  even if frame processing or display fails.
- Keep an IR example as comments, using the same explicit receive-and-display
  flow.

## Non-goals

- Do not change the public camera or processing APIs.
- Do not introduce a new display abstraction or support extra window features.

## Test Strategy

Test `main.main()` with the camera factory, processing function, and OpenCV
calls replaced by local fakes. Verify the RGB/depth arrays are passed to
`side_by_side()`, one image is displayed, `q` exits the loop, and both cleanup
calls execute. Removing the visualization module removes its wrapper tests.
