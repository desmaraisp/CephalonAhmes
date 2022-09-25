from src import (
    S3Utilities,
    ConfigurationHandler as cgh,
)
import boto3, pytest
from moto import mock_s3
from src.SubmissionsModels import IndividualSubmissionModel, SubmissionModelsForAllForumSources, SubmissionModelsForSingleForumSource

def test_fetch_cloudcube_contents_notfound():
    settings = cgh.S3Settings(
        PostHistoryFullFileName="File.json",
        S3_BucketName="TestBucket"
    )

    s3Utilities = S3Utilities.S3Utilities(settings)

    with mock_s3():
        conn = boto3.resource('s3')
        conn.create_bucket(Bucket=settings.S3_BucketName)
        
        result = s3Utilities.fetch_cloudcube_contents("File.json", "")

        assert(result=="")
    
def test_fetch_cloudcube_contents_found():
    settings = cgh.S3Settings(
        S3_BucketName="TestBucket"
    )

    s3Utilities = S3Utilities.S3Utilities(settings)

    with mock_s3():
        conn = boto3.resource('s3')
        conn.create_bucket(Bucket=settings.S3_BucketName)

        object = conn.Object(settings.S3_BucketName, 'File.txt')
        object.put(Body=b"BytesContent")
        
        result = s3Utilities.fetch_cloudcube_contents("File.txt", "")

        assert(result=="BytesContent")


def test_fetch_post_history_from_bucket_NotExist():
    settings = cgh.S3Settings(
        S3_BucketName="TestBucket",
        PostHistoryFullFileName="File.json"
    )

    s3Utilities = S3Utilities.S3Utilities(settings)

    with mock_s3():
        conn = boto3.resource('s3')
        conn.create_bucket(Bucket=settings.S3_BucketName)
        
        result = s3Utilities.fetch_post_history_from_bucket()

        assert(result.forum_sources == [])


def test_fetch_post_history_from_bucket_Exists():
    settings = cgh.S3Settings(
        S3_BucketName="TestBucket",
        PostHistoryFullFileName="File.json"
    )

    s3Utilities = S3Utilities.S3Utilities(settings)

    with mock_s3():
        conn = boto3.resource('s3')
        conn.create_bucket(Bucket=settings.S3_BucketName)

        model = SubmissionModelsForAllForumSources(
            forum_sources= [
                SubmissionModelsForSingleForumSource(
                    submission_source_forum_url= "url",
                    submissions_list= [
                        IndividualSubmissionModel(
                            submission_title="test",
                            submission_url="test"
                        )
                    ]
                )
            ]
        )

        s3Utilities.push_post_history_to_bucket(model)
        
        result = s3Utilities.fetch_post_history_from_bucket()

        assert(result == model)
