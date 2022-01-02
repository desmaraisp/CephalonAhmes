import src.Warframe_patchnotes_thief_script as wpts
import src.AhmesConfig as ahc
import json


Result = json.loads(wpts.fetch_cloudcube_contents(ahc.env_config["PostHistoryFileName"]))
print(json.dumps(Result, indent=4, sort_keys=True))

Result = wpts.fetch_cloudcube_contents("Log.txt")
print(Result)