# realsense-python

realsense d435i camera 셋업 및 재사용 가능한 함수 및 클래스 제공

## 카메라 연결 확인

RealSense 카메라가 연결되어 있는지 확인합니다.

```bash
uv run python doctor.py
```

카메라가 연결되어 있으면 이름·시리얼 번호·펌웨어 버전을 출력하고, 없으면 종료 코드 1로 실패합니다.

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

`q` 또는 `Esc`로도 녹화를 종료할 수 있습니다. 기본 캡처는 1280×720, 15 FPS이며, 필요하면 `--width`, `--height`, `--fps`를 지정합니다. USB3로 연결된 경우 `--fps 30`까지 가능합니다(USB2 연결에서는 1280×720 bgr8이 최대 15 FPS까지만 지원됩니다).

## D435i 지원 스트림 모드

아래 표는 현재 연결된 Intel RealSense D435i에서 확인한 지원 모드입니다. 이 프로젝트의 `start()`가 요청하는 포맷만 표시합니다.

### RGB (`bgr8`)

| 해상도 | 지원 FPS |
| --- | --- |
| 1920×1080 | 6, 15, 30 |
| 1280×720 | 6, 15, 30 |
| 960×540 | 6, 15, 30, 60 |
| 848×480 | 6, 15, 30, 60 |
| 640×480 | 6, 15, 30, 60 |
| 640×360 | 6, 15, 30, 60 |
| 424×240 | 6, 15, 30, 60 |
| 320×240 | 6, 30, 60 |
| 320×180 | 6, 30, 60 |

### Depth (`z16`)

| 해상도 | 지원 FPS |
| --- | --- |
| 1280×720 | 6, 15, 30 |
| 848×480 | 6, 15, 30, 60, 90 |
| 640×480 | 6, 15, 30, 60, 90 |
| 640×360 | 6, 15, 30, 60, 90 |
| 480×270 | 6, 15, 30, 60, 90 |
| 424×240 | 6, 15, 30, 60, 90 |
| 256×144 | 90, 300 |
| 848×100 | 100, 300 |

### IR 1 · IR 2 (`y8`)

| 해상도 | 지원 FPS |
| --- | --- |
| 1280×800 | 15, 30 |
| 1280×720 | 6, 15, 30 |
| 848×480 | 6, 15, 30, 60, 90 |
| 640×480 | 6, 15, 30, 60, 90 |
| 640×360 | 6, 15, 30, 60, 90 |
| 480×270 | 6, 15, 30, 60, 90 |
| 424×240 | 6, 15, 30, 60, 90 |
| 256×144 | 90, 300 |
| 848×100 | 100, 300 |

`512×512`는 지원하지 않습니다. 정사각형 결과가 필요하면 지원되는 해상도로 캡처한 뒤 중앙 크롭 또는 리사이즈하세요.

## IMU (가속도계 / 자이로) 사용하기

D435i는 가속도계(accel)와 자이로(gyro)를 내장하고 있습니다. `start()`에 `"imu"`(또는 개별로 `"accel"`, `"gyro"`)를 넣으면 RGB/Depth와 함께 활성화됩니다.

```python
from realsense_capture.camera import start
import pyrealsense2 as rs

camera = start("rgb", "depth", "imu", width=640, height=480, fps=30)

frames = camera.read()
frames.accel        # np.ndarray([x, y, z]) m/s^2, 정지 상태면 중력 방향으로 대략 9.8 크기
frames.gyro          # np.ndarray([x, y, z]) rad/s, 카메라 자체(body) 좌표계 기준 각속도
frames.timestamp_ms  # 이 프레임셋의 타임스탬프(ms) - 프레임 간 dt 계산용

# 자이로/가속도계 좌표계는 color/depth 광학 좌표계와 정확히 일치하지 않으므로,
# 각속도·가속도 벡터를 다른 스트림 좌표계로 옮기려면 외부 파라미터(extrinsics)를 적용해야 함
R, t = camera.imu_extrinsics(rs.stream.color)  # 자이로 좌표계 -> color 좌표계 회전/이동
```

**주의**: `rgb`/`depth` 같은 비디오 스트림과 `imu`를 같이 열 때는 `enable_stream`에 fps를 명시해야 합니다(생략하면 `Couldn't resolve requests`로 실패). `start()`는 내부적으로 `accel`/`gyro`를 200 FPS로 요청합니다.

**Linux 권한 설정 (최초 1회 필요)**: `pyrealsense2`를 pip/uv로만 설치하면 공식 librealsense udev 규칙이 시스템에 설치되지 않아, IMU 스트림을 열 때 다음처럼 실패합니다.

```text
RuntimeError: Failed to open scan_element .../scan_elements/in_anglvel_x_en Last Error: Permission denied
```

RGB/Depth는 표준 USB Video Class라 문제없지만, IMU는 Linux IIO(HID 센서) 서브시스템을 거치는데 이 경로의 권한이 기본적으로 `root`에게만 열려 있어서입니다. [librealsense 공식 udev 규칙](https://github.com/IntelRealSense/librealsense/blob/master/config/99-realsense-libusb.rules)을 설치하면 해결됩니다.

```bash
curl -fsSL https://raw.githubusercontent.com/IntelRealSense/librealsense/master/config/99-realsense-libusb.rules \
  -o /tmp/99-realsense-libusb.rules
sudo cp /tmp/99-realsense-libusb.rules /etc/udev/rules.d/99-realsense-libusb.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

규칙 적용 후 **USB 케이블을 뽑았다가 다시 꽂아야** 새 규칙이 이미 연결된 장치에도 반영됩니다.

## 다른 프로젝트에서 라이브러리로 쓰기

이 저장소는 `pyproject.toml`에 hatchling 빌드 설정이 있어 editable 설치가 가능합니다. 다른 uv 프로젝트(예: 형제 디렉터리의 `dynamic-GS`)에서:

```bash
uv add --editable ../realsense-python
```

이렇게 등록하면 `from realsense_capture.camera import start, Frames` 형태로 바로 import할 수 있습니다. 코드를 수정하면(editable이므로) 재설치 없이 즉시 반영됩니다.

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
