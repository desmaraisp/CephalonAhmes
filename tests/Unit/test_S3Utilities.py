from src import (
    S3Utilities,
    ConfigurationHandler as cgh,
)
import boto3, pytest
from moto import mock_s3
from src.Models import SubmissionModel, SubmissionListForMultipleSources, SubmissionsListForSingleSource
from datetime import datetime

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
        S3_BucketName="TestBucket",
        PostHistoryFullFileName="File.txt"
    )

    s3Utilities = S3Utilities.S3Utilities(settings)

    with mock_s3():
        conn = boto3.resource('s3')
        conn.create_bucket(Bucket=settings.S3_BucketName)

        object = conn.Object(settings.S3_BucketName, settings.PostHistoryFullFileName)
        object.put(Body=b"BytesContent")
        
        result = s3Utilities.fetch_cloudcube_contents(settings.PostHistoryFullFileName, "")

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

        model = SubmissionListForMultipleSources(
            forum_sources= [
                SubmissionsListForSingleSource(
                    rss_source_url= "url",
                    submissions_list= [
                        SubmissionModel(
                            title="test",
                            link="test",
                            contents="",
                            pub_date=datetime(year=20, month=3, day=19),
                            guid=123
                        )
                    ]
                )
            ]
        )

        s3Utilities.push_post_history_to_bucket(model)
        
        result = s3Utilities.fetch_post_history_from_bucket()

        assert(result == model)
