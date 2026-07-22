# realsense-python

realsense d435i camera 셋업 및 재사용 가능한 함수 및 클래스 제공


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