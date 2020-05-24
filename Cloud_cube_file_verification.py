import os
import boto3
session_cloudcube = boto3.Session(
	aws_access_key_id=os.environ["aws_access_key_id"],
    aws_secret_access_key=os.environ["aws_secret_access_key"],
)
s3 = session_cloudcube.resource('s3')
cloud_cube_object=s3.Object('cloud-cube',os.environ["cloud_cube_file_loc"])
print(cloud_cube_object.get()['Body'].read().decode('utf-8'))



# last_url='34'
# cloud_cube_object.put(Bucket='cloud-cube',Body=last_url.encode('utf-8'),Key='ls6cvw1eczmi/last_url_storage.txt')


