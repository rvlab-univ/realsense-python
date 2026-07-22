# realsense-python

realsense d435i camera 셋업 및 재사용 가능한 함수 및 클래스 제공

## 3DGS용 RGB 영상 캡처

원본 MP4와 해당 RGB 카메라의 intrinsic을 같은 장면 폴더에 저장한 뒤, 별도 후처리로 COLMAP용 JPG를 추출합니다. 촬영 중에는 장면은 고정하고 카메라를 천천히 움직여 인접 뷰가 충분히 겹치게 합니다.

```bash
uv run python capture_videosss.py --name desk_01 --duration 60
```

기본 출력은 다음과 같습니다.

```text
outputs/captures/desk_01/
├── video.mp4
├── intrinsics.json
└── capture.json
```

`q` 또는 `Esc`로도 녹화를 종료할 수 있습니다. 기본 캡처는 1280×720, 30 FPS이며, 필요하면 `--width`, `--height`, `--fps`를 지정합니다.

## COLMAP용 JPG 샘플링

원본 영상을 다시 촬영하지 않고 원하는 빈도로 프레임을 추출합니다. 3DGS/SfM에는 우선 5 Hz를 권장합니다.

```bash
uv run python postprocessing/sampler.py \
  --capture-dir outputs/captures/desk_01 \
  --fps 5
```

이 명령은 `images/`와 `sampling.json`을 추가합니다. 기존 `images/`가 있으면 덮어쓰지 않고 중단하므로, 다른 Hz로 다시 만들려면 새 장면 폴더를 쓰거나 기존 `images/`를 보관한 뒤 실행합니다.


## 카메라가 데이터 Matrix Shape 설명

- **RGB(Color)**
  - 각 픽셀의 색상값
  - 보통 shape: `(height, width, 3)`
  - 마지막 차원 3은 `[R, G, B]`, 각각 0~255 (`uint8`)
  - 예: `rgb[y, x] = [255, 0, 0]` → 빨강

- **Depth**
  - 각 픽셀에서 카메라까지의 거리
  - 보통 shape: `(height, width)` — 채널 없이 픽셀당 값 하나
  - 원본값은 흔히 `uint16`이고, 실제 미터 단위 거리는  
    `distance_m = depth[y, x] * depth_scale`
  - 예: depth 값이 `1000`, scale이 `0.001`이면 `1.0 m`
  - 값 `0`은 거리를 측정하지 못한 픽셀인 경우

- **IR (Infrared / 적외선)**
  - 적외선 카메라가 보는 흑백 영상. 사람 눈에는 안 보이는 적외선 빛의 반사 강도를 기록
  - 보통 shape: `(height, width)`이며 각 픽셀은 밝기 하나 (`uint8` 또는 `uint16`)
  - 값이 클수록 해당 위치에서 적외선 반사가 강해 더 밝게 보임
  - 깊이를 만드는 스테레오 카메라는 보통 좌/우 두 IR 이미지도 제공:
    - `IR left`: `(H, W)`
    - `IR right`: `(H, W)`
  - 두 IR 영상의 같은 물체 위치가 얼마나 어긋나는지(시차)를 이용해 depth를 계산

```text
RGB   : (H, W, 3)  → 색
Depth : (H, W)     → 거리
IR    : (H, W)     → 적외선 밝기(흑백)
```

주의: RGB와 Depth는 해상도와 카메라 위치가 다를 수 있음. 픽셀 좌표를 직접 대응시키려면 보통 depth를 color 화면 기준으로 맞추는 `align` 처리 필요
