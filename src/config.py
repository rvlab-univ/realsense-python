import pyrealsense2 as rs

def get_config():
    # 파이프라인 및 스트리밍 설정
    pipeline = rs.pipeline()
    config = rs.config()

    # 장치 연결 확인 및 RGB 센서 감지
    pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    pipeline_profile = config.resolve(pipeline_wrapper)
    device = pipeline_profile.get_device()

    found_rgb = False
    for s in device.sensors:
        if s.get_info(rs.camera_info.name) == 'RGB Camera':
            found_rgb = True
            break
    if not found_rgb:
        print("이 데모는 컬러 센서가 포함된 Depth 카메라가 필요합니다.")
        exit(0)

    # Depth 및 Color 스트림 활성화 (해상도 640x480, 30 FPS)
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    return pipeline, config