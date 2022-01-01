import pyaml_env as pyle

def Get_Config(Path):
	return pyle.parse_config(Path)

config = Get_Config('{}/../../Settings.ini'.format(__file__))

def Set_Configuration(ConfigurationName):
	try:
		global env_config
		env_config = config[ConfigurationName]
	except AttributeError:
		raise(Exception("No such environment"))

	for key in config["Shared"].keys():
		if key in env_config:
			env_config[key] = config["Shared"][key]


Set_Configuration('Default')

