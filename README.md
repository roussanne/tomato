# Tomato Harvest Automation

Intel RealSense D435 카메라와 AWS Rekognition 커스텀 라벨 모델을 이용해 토마토를 감지하고 숙성도를 판정한 뒤, Arduino 로봇 팔로 수확을 자동화하는 시스템입니다.

## 시스템 구성

```
RealSense D435 (RGB + Depth)
        ↓
이미지 전처리 (Homomorphic Filter)
        ↓
AWS Rekognition → 전체 토마토 감지
        ↓
적응형 색상 필터 (R-G 채널로 빨간색 강조)
        ↓
AWS Rekognition → 잘 익은 토마토만 재감지
        ↓
숙성도 판정: green / turning / lightred / red
        ↓
3D 좌표 (경계 상자 + 깊이 센서)
        ↓
Arduino 직렬 통신 → 로봇 팔 제어
```

## 하드웨어 요구사항

- NVIDIA Jetson (엣지 AI 처리)
- Intel RealSense D435 카메라
- Arduino (로봇 팔 제어)

## 소프트웨어 요구사항

```
boto3
opencv-python
numpy
pyrealsense2
Pillow
matplotlib
pyserial
```

## 환경 설정

`.env.example`을 복사해 `.env`를 만들고 실제 값을 입력합니다.

```bash
cp .env.example .env
```

`.env` 파일:

```
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=ap-northeast-2
AWS_REKOGNITION_MODEL_ARN=arn:aws:rekognition:...
AWS_REKOGNITION_PROJECT_ARN=arn:aws:rekognition:...
```

환경변수를 셸에 로드합니다:

```bash
export $(cat .env | xargs)
```

## 실행 방법

```bash
cd aws_tomato
python test.py
```

## 프로젝트 구조

```
aws_tomato/
├── test.py                                  # 진입점
├── amazon_rekognition_control/
│   ├── amazon_control.py                    # Rekognition 모델 시작/종료 클래스
│   ├── amazon_o.py                          # 모델 시작 유틸리티 (AWS 샘플 기반)
│   └── amazon_q.py                          # 모델 종료 유틸리티 (AWS 샘플 기반)
└── src/
    ├── filter/
    │   ├── img_filter.py                    # Homomorphic 필터, 히스토그램 정규화
    │   └── hist_eq.py                       # 히스토그램 등화 테스트 스크립트
    ├── jetson/
    │   ├── real_sense.py                    # RealSense 카메라 제어 (RGB + Depth)
    │   ├── mask.py                          # 토마토 감지 + 숙성도 판정 메인 모듈
    │   ├── tomato_mask_rgb.py               # RGB 기반 숙성도 판정 스크립트
    │   └── test.py                          # 테스트
    └── arduino/
        └── serial2arduino.py                # Arduino 직렬 통신
```

## 숙성도 분류 기준

Hue 채널 히스토그램의 가중 평균(`gaussian_mean`)을 다항식에 대입해 점수를 산출합니다.

```
base = 0.001 × gaussian_mean² - 0.2241 × gaussian_mean + 12.613
```

| 점수 범위 | 등급 | 의미 |
|-----------|------|------|
| base ≤ 1.5 | green | 덜 익음 |
| 1.5 < base ≤ 2.5 | turning | 변색 중 |
| 2.5 < base ≤ 3.5 | lightred | 거의 익음 |
| base > 3.5 | red | 완전히 익음 |
