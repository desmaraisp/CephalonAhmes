from Warframe_patchnotes_thief_script import start_cloudcube_session,fetch_cloudcube


cloud_cube_object=start_cloudcube_session()
print(fetch_cloudcube(cloud_cube_object))



# last_url='34'
# cloud_cube_object.put(Bucket='cloud-cube',Body=last_url.encode('utf-8'),Key=os.environ["cloud_cube_file_loc"])


