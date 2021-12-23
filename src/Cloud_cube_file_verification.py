from Warframe_patchnotes_thief_script import start_cloudcube_session,fetch_cloudcube_contents
import json


cloud_cube_object=start_cloudcube_session()
Result = fetch_cloudcube_contents(cloud_cube_object)
print(json.dumps(Result, indent=4, sort_keys=True))