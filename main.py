import pyrealsense2 as rs
import numpy as np
import cv2

from src.config import get_config


def main():
    pipeline, config = get_config()

    pipeline.start(config)

    try:
        while True:
            # Depth 프레임과 Color 프레임을 동기화하여 대기
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue

            # 프레임 데이터를 Numpy 배열로 변환
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # 깊이 데이터(16비트)를 눈으로 볼 수 있게 8비트로 변환하고 컬러맵 적용
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

            depth_colormap_dim = depth_colormap.shape
            color_colormap_dim = color_image.shape

            # Depth와 Color 해상도가 다를 경우 Color 이미지를 Depth 이미지 크기에 맞춰 리사이징
            if depth_colormap_dim != color_colormap_dim:
                resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
                images = np.hstack((resized_color_image, depth_colormap))
            else:
                images = np.hstack((color_image, depth_colormap))

            # OpenCV 창에 이미지 출력
            cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('RealSense', images)
            
            # 'q' 키나 'ESC' 키를 누르면 종료
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q') or key == 27:
                cv2.destroyAllWindows()
                break

    finally:
        pipeline.stop()

if __name__ == "__main__":
    main()