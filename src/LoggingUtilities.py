import logging
from src import (
        ConfigurationHandler as configuration_handler,
        S3BucketFunctions as s3b
)


def cap_log_string_length_in_lines(full_log_string: str, maximum_line_count: int):
    lines = full_log_string.split("\n")

    if len(lines) <= maximum_line_count:
        return full_log_string

    number_of_lines_to_cut = len(lines)-maximum_line_count
    lines = lines[number_of_lines_to_cut:]
    full_log_string = "\n".join(lines)
    return full_log_string


def commit_string_logger_to_bucket():
    log_string = logging.getLogger().handlers[1].stream.getvalue()
    log_string = s3b.fetch_cloudcube_contents(
            configuration_handler.PROJECTCONFIGURATION.LogFileName) + log_string
    log_string = cap_log_string_length_in_lines(log_string, 100)

    s3b.get_cloudcube_file_object(configuration_handler.PROJECTCONFIGURATION.LogFileName).put(
            Body=log_string.encode('utf-8')
    )
