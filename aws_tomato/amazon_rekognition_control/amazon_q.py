# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-custom-labels-developer-guide/blob/master/LICENSE-SAMPLECODE.)
"""AWS Rekognition 커스텀 라벨 모델 종료 유틸리티 (AWS 샘플 기반)."""

import os
import boto3


def stop_model(model_arn):
    """실행 중인 Rekognition 커스텀 라벨 모델을 중지한다."""
    client = boto3.client(
        'rekognition',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_REGION', 'ap-northeast-2'),
    )

    print('Stopping model:' + model_arn)

    try:
        response = client.stop_project_version(ProjectVersionArn=model_arn)
        status = response['Status']
        print('Status: ' + status)
    except Exception as e:
        print(e)

    print('Done...')


def main():
    """환경변수에서 ARN을 읽어 모델을 종료한다."""
    model_arn = os.environ.get('AWS_REKOGNITION_MODEL_ARN')
    stop_model(model_arn)


if __name__ == "__main__":
    main()