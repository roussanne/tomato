"""Intel RealSense D435 카메라에서 RGB 영상과 깊이 데이터를 수집하는 모듈."""

import cv2
import numpy as np
import pyrealsense2 as rs
import time


def rgb_depth():
    """RealSense 카메라를 15프레임 구동해 깊이 데이터(2D 리스트)와 컬러 이미지를 반환한다."""
    # RealSense pipeline 설정
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640,480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640,480, rs.format.bgr8, 30)

    # 파이프라인 시작
    profile = pipeline.start(config)

    cnt = 15

    try:
        while cnt:
            # 프레임 가져오기
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            # 프레임이 없으면 건너뛰기
            if not depth_frame:
                continue

            if not color_frame:
                continue

            color = np.asanyarray(color_frame.get_data())
            color_image = color

            # 깊이 데이터를 넘파이 배열로 변환
            depth = rs.colorizer().colorize(depth_frame)
            depth_image = np.asanyarray(depth.get_data())

            # 특정 좌표의 객체의 depth정보를 2차원 배열에 저장
            width = depth_image.shape[0]
            height = depth_image.shape[1]

            depth_data = [[0 for i in range(width)] for j in range(height)]

            for i in range(0, width):
                for j in range(0, height):
                    depth_data[j][i] = depth_frame.get_distance(j,i)


            # 깊이 데이터 표시
            cv2.imshow('Depth Image', depth_image)
            # 컬러 데이터 표시
            cv2.imshow('Color Image', color_image)

            # print(type(color_image))

            cv2.imwrite('./result_image/depth.jpg', depth_image)
            cv2.imwrite('./result_image/color.jpg', color_image)

            # print(type(color_image))

            # time.sleep(3)
            cnt -= 1


            # 'q' 키를 누르면 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


    finally:
        # 종료 시 리소스 해제
        pipeline.stop()
        cv2.destroyAllWindows()
        return depth_data, color_image

if __name__ == "__main__":
    rgb_depth()
