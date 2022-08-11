from src import (
    LoggingUtilities,
    S3BucketFunctions as s3b,
    ConfigurationHandler as configuration_handler
)
import boto3, logging, logging.config
from moto import mock_s3

def test_cull_logs():
    initial_string = "test1 \n test2 \n test3 \n test4"

    Expected = " test2 \n test3 \n test4"

    Result = LoggingUtilities.cap_log_string_length_in_lines(initial_string, 3)

    assert Result == Expected
    
def test_commit_string_logger_to_bucket():
    logging.config.fileConfig(
        configuration_handler.PROJECTCONFIGURATION.LoggingConfigFileName)
    
    logging.getLogger().error("Hello world!")
    with mock_s3():
        conn = boto3.resource('s3')
        conn.create_bucket(Bucket='cloud-cube')

        LoggingUtilities.commit_string_logger_to_bucket()
        
        body = s3b.get_cloudcube_file_object(configuration_handler.PROJECTCONFIGURATION.LogFileName).get()['Body'].read().decode("utf-8")
    assert('Hello world!' in body)
