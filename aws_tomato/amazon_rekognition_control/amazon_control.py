import boto3

class AmazonControl:
    
    # 생성자 -> 아마존 서비스에 필요한 변수들을 저장할 곳
    def __init__(self):
        self.aws_access_key_id = "id"
        self.aws_secret_access_key = 'key'
        self.region_name = 'ap-northeast-2'
        self.min_inference_units=1 
        self.version_name='CherryTomato.2023-12-01T16.17.45'
        self.model_arn = 'arn:aws:rekognition:ap-northeast-2:104468943122:project/CherryTomato/version/CherryTomato.2023-12-01T16.17.45/1701418665992'

    # 아마존 Rekognition의 사용을 시작하기 위한 코드
    def start_rekognition(self):
        client = boto3.client('rekognition', aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key, region_name=self.region_name)

        try:
            # 모델 시작하기 어떤 모델을 동작할건지 출력
            print('Starting model: ' + self.model_arn)
            response=client.start_project_version(ProjectVersionArn=self.model_arn, MinInferenceUnits=self.min_inference_units)
            # 모델이 동작할 때 까지 기다린다.
            project_version_running_waiter = client.get_waiter('project_version_running')
            project_version_running_waiter.wait(ProjectArn=self.project_arn, VersionNames=[self.version_name])
            #Get the running status
            describe_response=client.describe_project_versions(ProjectArn=self.project_arn,
                VersionNames=[self.version_name])
            for model in describe_response['ProjectVersionDescriptions']:
                print("Status: " + model['Status'])
                print("Message: " + model['StatusMessage']) 
        except Exception as e:
            print(e)
            
        print('Done...')

    def stop_rekognition(self):

        client = boto3.client('rekognition', aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key, region_name=self.region_name)

        print('Stopping model:' + self.model_arn)

        #Stop the model
        try:
            response=client.stop_project_version(ProjectVersionArn=self.model_arn)
            status=response['Status']
            print ('Status: ' + status)
        except Exception as e:  
            print(e)  

        print('Done...')

