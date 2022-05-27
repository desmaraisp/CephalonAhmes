import boto3, json
from botocore.errorfactory import ClientError
from src import (
    ConfigurationHandler as configuration_handler,
    SubmissionsModels as models,
    DataclassConversions,
)


def get_cloudcube_file_object(filename: str):
    session_cloudcube = boto3.Session(
        aws_access_key_id=configuration_handler.PROJECTCONFIGURATION.CLOUDCUBE_ACCESS_KEY_ID,
        aws_secret_access_key=configuration_handler.PROJECTCONFIGURATION.CLOUDCUBE_SECRET_ACCESS_KEY,
    )
    s3 = session_cloudcube.resource('s3')

    return s3.Object('cloud-cube',configuration_handler.PROJECTCONFIGURATION.CLOUD_CUBE_BASE_LOC+filename)


def fetch_cloudcube_contents(filename: str, default_contents: str = '') -> str:
    try:
        cloud_cube_object = get_cloudcube_file_object(filename).get()

    except ClientError as e:
        if e.response['ResponseMetadata']['HTTPStatusCode'] == 404:
            return default_contents

        else:
            raise e

    return cloud_cube_object['Body'].read().decode('utf-8')

def fetch_post_history_from_bucket() -> models.SubmissionModelsForAllForumSources:
    PostHistory_json = json.loads(fetch_cloudcube_contents(
            configuration_handler.PROJECTCONFIGURATION.PostHistoryFileName,
            "{}"
        )
    )

    return DataclassConversions.convert_post_history_json_to_submission_model(PostHistory_json)

def push_post_history_to_bucket(post_history: models.SubmissionModelsForAllForumSources):

    post_history_json : dict = DataclassConversions.convert_post_history_model_to_json(post_history)

    get_cloudcube_file_object(configuration_handler.PROJECTCONFIGURATION.PostHistoryFileName).put(
        Body=json.dumps(post_history_json).encode('utf-8')
        )