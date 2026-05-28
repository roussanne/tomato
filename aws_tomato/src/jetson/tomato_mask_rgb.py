"""RGB 이미지에서 R-G 차이 마스크와 Hue 히스토그램으로 토마토 숙성도를 판정하는 스크립트."""

import cv2
import numpy as np
import math
from matplotlib import pyplot as plt


def ripeness(each_tomato):
    """0이 아닌 Hue 값의 가중 평균을 이용해 숙성도("green"/"turning"/"lightred"/"red")를 반환한다."""
    hsv_tomato = cv2.cvtColor(each_tomato, cv2.COLOR_BGR2HSV)

    hue_channel = hsv_tomato[:,:,0]
    hue_nonzero_channel = hue_channel[hue_channel != 0]

    hist = np.histogram(hue_nonzero_channel, bins=256, range=(0, 255))[0]

    gaussian_mean = np.sum(hist * np.arange(256)) / np.sum(hist)

    print(gaussian_mean)

    base = 0.001 * pow(gaussian_mean, 2) - 0.2241 * gaussian_mean + 12.613

    print(base)
    
    plt.plot(hist)
    plt.show()

    if base <= 1.5:
        return "green"
    elif base > 1.5 and base <= 2.5:
        return "turning"
    elif base > 2.5 and base <= 3.5:
        return "lightred"
    elif base > 3.5:
        return "red"
    

# 이미지 불러오기
# 해당 이미지는 BGR 포맷이다.
img = cv2.imread("./image/171.jpg")

# 흑백 이미지로 변환하기
g_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# hsv 스케일을 가지는 이미지로 변환하기
hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

# 잡음 제거 코드
# kernel = np.ones((7, 7), np.uint8)
# g_img = cv2.morphologyEx(g_img, cv2.MORPH_OPEN, kernel, iterations=2)

# 흑백 이미지와 똑같은 크기의 빈 이미지 행렬을 생성, 행렬의 원소는 0이다.
zero = np.zeros_like(g_img)

# 이중 반복문을 돌리기 위한 width 와 height를 얻기위한 코드
w = g_img.shape[1]
h = g_img.shape[0]

# print(img[137][108][2])
# print(img[137][108][1])
# print((int(img[137][108][2]) - int(img[137][108][1])))
# print(146 - 156)

print(img[244][300][2])

# 이중 반복문을 돌면서 r-g, b-g 의 픽셀 연산을 통해 적절한 마스크를 생성
# r-g = red를 돋보이게
# b-g = green을 돋보이게
for i in range(0, w):
    for j in range(0, h):
        # r-g 빨강 탐색에 최적화 다익은 토마토
        zero[j][i] = (np.float32(math.exp(abs(int(img[j][i][2]) - int(img[j][i][1])))) - 1.0)
        # g-b 초록 탐색에 최적화 덜익은 토마토
        # zero[j][i] = (np.float64(math.exp(abs(int(img[j][i][0]) - int(img[j][i][1])))) - 1.0)

# 250에서 255의 값만 그 값 그대로 취하고 나머지 값은 0으로 바꾸는 이진화 코드
bin_img = cv2.inRange(zero, 254, 255)

# 비트 연산자를 적용하기 위해 이중 반복문으로 255 -> 1 로 바꿔준 코드
# for i in range(0, w):
#     for j in range(0, h):
#         if bin_img[j][i] == 255:
#             bin_img[j][i] = 1
#         else:
#             bin_img[j][i] = 0

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

# 각 색 영역에 대한 mask 생성
red_mask = cv2.inRange(hsv, lower_red, upper_red)
green_mask = cv2.inRange(hsv, lower_green, upper_green)
lime_mask = cv2.inRange(hsv, lower_lime, upper_lime)
yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

# bin_img = bin_img - green_mask

# 3차원 이미지로 만들어 픽셀단위 마스킹 연산을 하기 위해 이미지 행렬을 생성한 코드
# bin_img = cv2.cvtColor(bin_img, cv2.COLOR_GRAY2BGR)

# 침식 과정을 수행하기 위한 커널 생성
kernel = np.ones((20, 20), np.uint8)

# 침식 알고리즘 적용 코드
erode_img = cv2.erode(bin_img, kernel)

dilate_img = cv2.dilate(erode_img, kernel)
ret, dilate_img = cv2.threshold(dilate_img, 170, 255, cv2.THRESH_BINARY)

mask =  bin_img - green_mask
ret, mask = cv2.threshold(mask, 170, 255, cv2.THRESH_BINARY)
mask_ = cv2.bitwise_and(mask, dilate_img)

mask_ = cv2.cvtColor(mask_, cv2.COLOR_GRAY2RGB)

result = cv2.bitwise_and(img, mask_)

hist = cv2.calcHist([zero], [0], None, [256], [0,256])

# hsv_result = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)

ripe = ripeness(result)

print(ripe)


# for i in range(0,w):
#     for j in range(0,h):
#         if hsv_result[j][i][1] != 0:
#             hsv_result[j][i][1] = 100

hsv_result = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)

cv2.imshow("result", result)
# cv2.imshow("result1", img)
# cv2.imshow("result2", mask)
cv2.imshow("hsv", hsv_result)

cv2.waitKey()
# plt.plot(hist)
# plt.show()

cv2.destroyAllWindows()