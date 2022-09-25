import boto3, json
from botocore.errorfactory import ClientError
from src import (
    ConfigurationHandler as cgh,
    SubmissionsModels as models,
    DataclassConversions
)

class S3Utilities:
    settings: cgh.S3Settings
    
    def __init__(self, settings: cgh.S3Settings) -> None:
        self.settings = settings


    def get_cloudcube_file_object(self, filename: str):
        session_cloudcube = boto3.Session()
        s3 = session_cloudcube.resource('s3')

        return s3.Object(self.settings.S3_BucketName,filename)


    def fetch_cloudcube_contents(self, filename: str, default_contents: str = '') -> str:
        try:
            cloud_cube_object = self.get_cloudcube_file_object(filename).get()

        except ClientError as e:
            if e.response['ResponseMetadata']['HTTPStatusCode'] == 404:
                return default_contents

            else:
                raise e

        return cloud_cube_object['Body'].read().decode('utf-8')

    def fetch_post_history_from_bucket(self) -> models.SubmissionModelsForAllForumSources:
        PostHistory_json = json.loads(self.fetch_cloudcube_contents(
                self.settings.PostHistoryFullFileName,
                "{}"
            )
        )
        return DataclassConversions.convert_post_history_json_to_submission_model(PostHistory_json)

    def push_post_history_to_bucket(self, post_history: models.SubmissionModelsForAllForumSources):
        post_history_json : dict = DataclassConversions.convert_post_history_model_to_json(post_history)

        self.get_cloudcube_file_object(self.settings.PostHistoryFullFileName).put(
            Body=json.dumps(post_history_json).encode('utf-8')
            )
