import pyaml_env as pyle
import os

def Get_Config(Path):
	return pyle.parse_config(Path)

config = Get_Config('{}/../../Settings.ini'.format(__file__))

def Set_Configuration(ConfigurationName):
	try:
		new_env_dict = config[ConfigurationName]
	except AttributeError:
		raise(Exception("No such environment"))

	for key in config["Default"].keys():
		if key not in new_env_dict:
			new_env_dict[key] = config["Default"][key]
			
	global env_config
	env_config = new_env_dict


if os.environ["ConfigurationName"]:
	Set_Configuration(os.environ["ConfigurationName"])
else 	Set_Configuration("Default")

