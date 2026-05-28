"""AWS Rekognition 커스텀 라벨 모델의 시작과 종료를 관리하는 모듈."""

import os
import boto3


class AmazonControl:
    """AWS Rekognition 커스텀 라벨 모델을 제어하는 클래스."""

    def __init__(self):
        """환경변수에서 AWS 인증 정보와 모델 ARN을 읽어 초기화한다."""
        self.aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.region_name = os.environ.get('AWS_REGION', 'ap-northeast-2')
        self.min_inference_units = 1
        self.version_name = 'CherryTomato.2023-12-01T16.17.45'
        self.model_arn = os.environ.get('AWS_REKOGNITION_MODEL_ARN')
        self.project_arn = os.environ.get('AWS_REKOGNITION_PROJECT_ARN')

    def start_rekognition(self):
        """Rekognition 커스텀 라벨 모델을 시작하고 Running 상태가 될 때까지 대기한다."""
        client = boto3.client('rekognition', aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key, region_name=self.region_name)

        try:
            print('Starting model: ' + self.model_arn)
            client.start_project_version(ProjectVersionArn=self.model_arn, MinInferenceUnits=self.min_inference_units)
            project_version_running_waiter = client.get_waiter('project_version_running')
            project_version_running_waiter.wait(ProjectArn=self.project_arn, VersionNames=[self.version_name])
            describe_response = client.describe_project_versions(ProjectArn=self.project_arn, VersionNames=[self.version_name])
            for model in describe_response['ProjectVersionDescriptions']:
                print("Status: " + model['Status'])
                print("Message: " + model['StatusMessage'])
        except Exception as e:
            print(e)

        print('Done...')

    def stop_rekognition(self):
        """실행 중인 Rekognition 커스텀 라벨 모델을 중지한다."""
        client = boto3.client('rekognition', aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key, region_name=self.region_name)

        print('Stopping model:' + self.model_arn)

        try:
            response = client.stop_project_version(ProjectVersionArn=self.model_arn)
            status = response['Status']
            print('Status: ' + status)
        except Exception as e:
            print(e)

        print('Done...')

