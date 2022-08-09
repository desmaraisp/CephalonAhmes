from src import (S3BucketFunctions, DataclassConversions)
import json

print("Post History - Test")
Result = DataclassConversions.convert_post_history_json_to_submission_model(
        json.loads(S3BucketFunctions.fetch_cloudcube_contents("SubmissionHistory.Default.json", "{}"))
)
print(Result)

print("==========\n\nPost History - Live")
Result = DataclassConversions.convert_post_history_json_to_submission_model(
    json.loads(S3BucketFunctions.fetch_cloudcube_contents("SubmissionHistory.Live.json", "{}"))
)
print(Result)


print("==========\n\nTest Error Log")
Result = S3BucketFunctions.fetch_cloudcube_contents("Default.log")
print(Result)

print("==========\n\nProduction Error Log")
Result = S3BucketFunctions.fetch_cloudcube_contents("Live.log")
print(Result)
