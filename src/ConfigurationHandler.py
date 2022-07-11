import ProjectSettings
import os

current_configuration_name = os.getenv('ConfigurationName', 'Default')

if(current_configuration_name not in ProjectSettings.ConfigurationClasses):
    raise(Exception("No such environment : {}".format(current_configuration_name)))

_klass = ProjectSettings.ConfigurationClasses[current_configuration_name]
PROJECTCONFIGURATION: ProjectSettings.Default = _klass()
