import ProjectSettings
import os

current_configuration_name = os.getenv('ConfigurationName', 'Default')

try:
    _klass = getattr(ProjectSettings, current_configuration_name)
except AttributeError:
    raise(Exception("No such environment"))

PROJECTCONFIGURATION: ProjectSettings.Default = _klass()
