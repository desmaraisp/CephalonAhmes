import src.Warframe_patchnotes_thief_script as wpts
import src.AhmesConfig as ahc
import json


Result = json.loads(wpts.fetch_cloudcube_contents("PostHistory.json"))
print(json.dumps(Result, indent=4, sort_keys=True))

print("==========\n")

Result = wpts.fetch_cloudcube_contents("Log.txt")
print(Result)

print("==========\n")

Result = wpts.fetch_cloudcube_contents("Ahmes.log")
print(Result)
