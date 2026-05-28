"""AWS Rekognition 모델 시작/종료 진입점."""

from amazon_rekognition_control.amazon_control import AmazonControl


def main():
    """Rekognition 커스텀 라벨 모델을 시작한다."""
    amazon = AmazonControl()
    amazon.start_rekognition()
    # amazon.stop_rekognition()


if __name__ == "__main__":
    main()