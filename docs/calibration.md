직접 코드를 만드려 했는데, 그것보다는 공식 따르는게 맞지!
그래서 보정하는 방법 물어봤다.



네. **코드를 직접 작성하기보다 공식 RealSense Viewer를 설치해 보정하는 것이 가장 좋습니다.** D435i 자체에 보정값을 저장할 수 있고, 실패하면 공장 출하값으로 되돌릴 수도 있습니다.

다만 D435i에는 서로 다른 보정이 있습니다.

- Depth 보정: 좌·우 적외선 스테레오 카메라 → `On-Chip Calibration`
- 거리 보정: 실제 거리 오차 → `Tare Calibration`
- IMU 보정: 가속도계·자이로 → 별도의 `rs-imu-calibration.py`
- RGB–Depth 정렬 보정: 일반적인 On-Chip 보정과 별개이며 필요할 때만 Dynamic Calibrator 사용

오늘은 우선 **Depth On-Chip Calibration**만 진행하는 것을 추천합니다.

## 1. 공식 Viewer 설치

Ubuntu 20.04/22.04/24.04 LTS라면 공식 패키지를 이용하는 것이 편합니다. 현재 공식 저장소는 IntelRealSense에서 `realsenseai`로 이전되었습니다. [공식 Ubuntu 설치 안내](https://github.com/realsenseai/librealsense/blob/master/doc/distribution_linux.md)

```bash
sudo mkdir -p /etc/apt/keyrings

curl -sSf https://librealsense.realsenseai.com/Debian/librealsenseai.asc \
  | gpg --dearmor \
  | sudo tee /etc/apt/keyrings/librealsenseai.gpg > /dev/null

sudo apt-get install apt-transport-https

echo "deb [signed-by=/etc/apt/keyrings/librealsenseai.gpg] https://librealsense.realsenseai.com/Debian/apt-repo $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/librealsense.list

sudo apt-get update
sudo apt-get install librealsense2-dkms librealsense2-utils
```

카메라를 USB 3 포트에 다시 연결한 뒤 실행합니다.

```bash
realsense-viewer
```

이미 설치되어 있다면 바로 Viewer를 실행하면 됩니다. 소스 빌드나 Python 코드는 필요 없습니다.

## 2. 보정 전 확인

보정은 카메라가 실제로 다음 증상을 보일 때 진행하는 게 좋습니다.

- 평평한 벽의 깊이 영상이 울퉁불퉁함
- 깊이 데이터가 평소보다 많이 비어 있음
- 실측 거리와 측정 거리가 약 3% 이상 차이 남
- 충격이나 온도 변화 이후 품질이 나빠짐

문제가 없다면 공장 보정값을 그대로 쓰는 편이 낫습니다.

Viewer에서 먼저 다음을 확인하세요.

1. 펌웨어를 Viewer가 권장하는 버전으로 업데이트
2. USB 연결이 `3.x`인지 확인
3. Depth 스트림을 켜고 평평하고 질감이 있는 벽을 촬영
4. 현재 상태를 눈으로 확인하거나 Depth Quality Tool로 측정

## 3. On-Chip Calibration 실행

Viewer의 D435i 장치 메뉴에서 다음과 비슷한 경로를 찾습니다.

```text
More / Calibration
→ On-Chip Calibration
```

Viewer 버전에 따라 메뉴 표현은 조금 다를 수 있습니다.

실행 환경은 다음처럼 잡으세요.

- 카메라 앞 약 1~2m에 평평한 장면 배치
- 완전히 하얀 민무늬 벽보다는 사물이나 질감이 조금 있는 장면 사용
- 적절히 밝고 반사나 직사광선이 없는 실내
- USB 3 연결
- 실행 중 카메라와 장면을 크게 움직이지 않기
- 다른 RealSense 프로그램과 ROS 노드는 종료

보정이 끝나면 새 값이 바로 영구 저장되는지 확인하고, 결과가 좋아졌을 때만 `Apply` 또는 `Write`를 선택하세요. 가능하면 먼저 `Health Check` 결과와 깊이 영상을 비교해야 합니다. 공식 설명상 On-Chip Self-Calibration은 별도 체커보드 없이 수행할 수 있습니다. [공식 Self-Calibration 설명](https://dev.realsenseai.com/stereo-depth/self-calibration-for-depth-cameras/)

결과가 오히려 나쁘다면 저장하지 않거나 Viewer에서 `Restore Factory Calibration`으로 되돌리면 됩니다.

## 4. IMU도 이상할 때만 별도 보정

D435i의 가속도계가 정지 상태에서 크게 치우치거나 자세 추정이 이상하다면 공식 IMU 도구를 사용합니다.

- 공식 도구: `rs-imu-calibration.py`
- 카메라를 안내에 따라 6개 면으로 놓아서 측정
- 계산된 값을 확인한 다음 장치에 기록

[공식 D435i IMU Calibration Tool](https://dev.realsenseai.com/download/18539/)

일반적인 Depth 품질 문제라면 IMU 보정은 필요 없습니다.

결론적으로 오늘의 추천 순서는:

```text
RealSense Viewer 설치
→ 현재 Depth 품질 확인
→ 문제가 있을 때만 On-Chip Calibration
→ 전후 결과 비교
→ 좋아졌을 때만 저장
```

이 저장소에는 나중에 필요하면 **보정값 조회와 Depth 거리 검증만 하는 아주 짧은 Python 함수**를 추가하면 충분합니다. 실제 보정 알고리즘까지 구현할 필요는 없습니다.