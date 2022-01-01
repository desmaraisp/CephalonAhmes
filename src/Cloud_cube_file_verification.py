import Warframe_patchnotes_thief_script as wpts
import json


Result = json.loads(wpts.fetch_cloudcube_contents("PostHistory.json"))
print(json.dumps(Result, indent=4, sort_keys=True))