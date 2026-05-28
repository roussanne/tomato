import os
import cv2
import math
import boto3
import io
import time
import numpy as np
import pyrealsense2 as rs
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont
from real_sense import rgb_depth
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from filter.img_filter import homomorphic_filter, histogram_normalize

# 빨간색의 범위 지정
lower_red = np.array([0, 100, 100])
upper_red = np.array([10, 255, 255])

# 초록색의 범위 지정
lower_green = np.array([40, 40, 40])
upper_green = np.array([80, 255, 255])

# 연두색의 범위 지정
lower_lime = np.array([35, 40, 40])
upper_lime = np.array([80, 255, 255])

# 노란색의 범위 지정
lower_yellow = np.array([20, 100, 100])
upper_yellow = np.array([40, 255, 255])


def rank():
    return ""

def ripeness(each_tomato):

    hsv_tomato = cv2.cvtColor(each_tomato, cv2.COLOR_BGR2HSV)

    hue_channel = hsv_tomato[:,:,0]
    hist = cv2.calcHist([hue_channel], [0], None, [256], [0,256])
    
    kernel = cv2.getGaussianKernel(5, 1)
    
    smoothed_hist = cv2.filter2D(hist, -1, kernel)
    max_value = np.max(smoothed_hist)
    max_index = np.argmax(smoothed_hist)

    gaussian_mean = max_index * (256 / len(smoothed_hist))

    base = 0.001 * pow(gaussian_mean, 2) - 0.2241 * gaussian_mean + 12.613

    if base <= 1.5:
        return "green"
    elif base > 1.5 and base <= 2.5:
        return "turning"
    elif base > 2.5 and base <= 3.5:
        return "lightred"
    else:
        return "red"
    

def roi():
    return ""

def find_tomato(rekognition_client, model, origin_frame):
    
    # if id == "first":
    #     origin_frame = cv2.imread("./image/mixed_tomato_1.jpg")
        
    frame = np.asanyarray(origin_frame)
    _, img_encoded = cv2.imencode('.jpg', frame)
    img_bytes = img_encoded.tobytes()

    response = rekognition_client.detect_custom_labels(
        Image = {'Bytes' : img_bytes},
        MinConfidence = 40,
        ProjectVersionArn = model
    )

    imgWidth = frame.shape[1]
    imgHeight = frame.shape[0]
    frame_pil = Image.fromarray(np.uint8(frame))
    draw = ImageDraw.Draw(frame_pil)

    point_data = []

    print("Detected labels:")
    
    for customLabel in response['CustomLabels']:
        cnt = 0
        print('Label ' + str(customLabel['Name']))
        print('Confidence ' + str(customLabel['Confidence']))

        if 'Geometry' in customLabel:
            box = customLabel['Geometry']['BoundingBox']
            left = imgWidth * box['Left']
            top = imgHeight * box['Top']
            width = imgWidth * box['Width']
            height = imgHeight * box['Height']

            center_point_x = left + width/2
            center_point_y = top + height/2

            # depth_data = depth(center_point_x, center_point_y)
            point_depth = {
                'left': left, 'top': top,
                'width': width, 'height': height,
                'center_x': center_point_x, 'center_y': center_point_y
            }

            print(point_depth)

            point_data.append(point_depth)

            fnt = ImageFont.load_default()
            draw.text((left, top), customLabel['Name'], fill = '#00d400', font=fnt)

            points = (
                    (left, top),
                    (left + width, top),
                    (left + width, top + height),
                    (left, top + height),
                    (left, top)
            )
            draw.line(points, fill='#00d400', width=5)

    frame = np.array(frame_pil)
    print(len(point_data))
    cv2.imshow("cam", frame)
    cv2.waitKey(5000)
    return point_data, frame

def adapt_filter(frame):

    gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    zero = np.zeros_like(gray_img)

    w = gray_img.shape[1]
    h = gray_img.shape[0]

    for i in range(0, w):
        for j in range(0, h):
            zero[j][i] = (np.float64(math.exp(abs(int(frame[j][i][2]) - int(frame[j][i][1])))) - 1.0)

    bin_img = cv2.inRange(zero, 254, 255)

    kernel = np.ones((20, 20), np.uint8)

    erode_img = cv2.erode(bin_img, kernel)

    kernel = np.ones((50, 50), np.uint8)

    dilate_image = cv2.dilate(erode_img, kernel)
    _, dilate_image = cv2.threshold(dilate_image, 170, 255, cv2.THRESH_BINARY)

    # red_mask = cv2.inRange(hsv_img, lower_red, upper_red)
    lime_mask = cv2.inRange(hsv_img, lower_lime, upper_lime)
    yellow_mask = cv2.inRange(hsv_img, lower_yellow, upper_yellow)
    
    green_mask = cv2.inRange(hsv_img, lower_green, upper_green)

    mask = bin_img - green_mask - yellow_mask - lime_mask
    _, mask = cv2.threshold(mask, 170, 255, cv2.THRESH_BINARY)
    
    mask = cv2.medianBlur(mask, 9)

    final_mask = cv2.bitwise_and(mask, dilate_image)

    # final_mask = np.zeros_like(mask)

    # width = mask.shape[1]
    # height = mask.shape[0]

    # for i in range(width):
    #     for j in range(height):
    #         if mask[j][i] == 0 and dilate_image[j][i] == 0:
    #             final_mask[j][i] = 255


    cv2.imshow("mask", mask)
    cv2.imshow("dilate", dilate_image)

    kernel = np.ones((20, 20), np.uint8)

    final_dilate_mask = cv2.dilate(final_mask, kernel)

    cv2.imshow("final_mask", final_dilate_mask)
    cv2.waitKey()

    final_mask = cv2.cvtColor(final_dilate_mask, cv2.COLOR_GRAY2BGR)

    result = cv2.bitwise_and(frame, final_mask)

    hist = cv2.calcHist([zero], [0], None, [256], [0, 256])

    return result


def find_red_tomato(rekognition_client, model, first_frame):

    #Red ( 잘 익은 토마토 ) 를 찾기위한 필터
    # origin_frame = cv2.imread("./image/mixed_tomato_1.jpg")
    # frame = adapt_filter(origin_frame)
    frame = adapt_filter(first_frame)

    second_point_data, second_frame = find_tomato(rekognition_client, model, frame)

    cv2.imshow("second_frame", second_frame)
    cv2.waitKey()

    return second_point_data, second_frame


def calc_difference(first_point_data, second_point_data):

    ripen_tomato = []

    for i in range(0, len(first_point_data)):
        for j in range(0, len(second_point_data)):
            if first_point_data[i] != second_point_data[j]:
                ripen_tomato.append(first_point_data[i])

    unripen_tomato = second_point_data

    return ripen_tomato, unripen_tomato

def main():
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    region_name = os.environ.get('AWS_REGION', 'ap-northeast-2')
    model = os.environ.get('AWS_REKOGNITION_MODEL_ARN')

    rekognition_client = boto3.client('rekognition', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)

    # RealSense 카메라를 활용한 depth데이터와 RGB데이터 수집
    depth, frame = rgb_depth()

    # 수집한 영상의 조명에의한 간섭을 제거하는 코드
    # frame = homomorphic_filter(frame)
    # frame = histogram_normalize(frame)

    first_point_data, first_frame = find_tomato(rekognition_client, model, frame)

    second_point_data, second_frame = find_red_tomato(rekognition_client, model, frame)

    ripen_tomato, unripen_tomato = calc_difference(first_point_data, second_point_data)

    ripeness(unripen_tomato)

if __name__ == '__main__':
    main()