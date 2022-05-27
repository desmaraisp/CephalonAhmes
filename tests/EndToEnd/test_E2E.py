import src.main as wpts
import src.ConfigurationHandler as configuration_handler
import pytest

@pytest.mark.E2E
def test_main_loop():
    wpts.main_loop(configuration_handler.PROJECTCONFIGURATION.MaxIterations,
            configuration_handler.PROJECTCONFIGURATION.Iteration_Interval_Time,
            )


