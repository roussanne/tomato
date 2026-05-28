# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-custom-labels-developer-guide/blob/master/LICENSE-SAMPLECODE.)
"""AWS Rekognition 커스텀 라벨 모델 시작 유틸리티 (AWS 샘플 기반)."""

import os
import boto3


def start_model(project_arn, model_arn, version_name, min_inference_units):
    """Rekognition 커스텀 라벨 모델을 시작하고 Running 상태가 될 때까지 대기한다."""
    client = boto3.client(
        'rekognition',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_REGION', 'ap-northeast-2'),
    )

    try:
        print('Starting model: ' + model_arn)
        client.start_project_version(ProjectVersionArn=model_arn, MinInferenceUnits=min_inference_units)
        project_version_running_waiter = client.get_waiter('project_version_running')
        project_version_running_waiter.wait(ProjectArn=project_arn, VersionNames=[version_name])

        describe_response = client.describe_project_versions(ProjectArn=project_arn, VersionNames=[version_name])
        for model in describe_response['ProjectVersionDescriptions']:
            print("Status: " + model['Status'])
            print("Message: " + model['StatusMessage'])
    except Exception as e:
        print(e)

    print('Done...')


def main():
    """환경변수에서 ARN을 읽어 모델을 시작한다."""
    project_arn = os.environ.get('AWS_REKOGNITION_PROJECT_ARN')
    model_arn = os.environ.get('AWS_REKOGNITION_MODEL_ARN')
    min_inference_units = 1
    version_name = 'CherryTomato.2023-12-01T16.17.45'
    start_model(project_arn, model_arn, version_name, min_inference_units)


if __name__ == "__main__":
    main()