from src import (
        main as wpts,
        S3BucketFunctions as s3b,
        ConfigurationHandler as configuration_handler,
        
)
import pytest

@pytest.mark.E2E
def test_main_loop():
    s3b.get_cloudcube_file_object(configuration_handler.PROJECTCONFIGURATION.PostHistoryFileName).delete()
    
    wpts.main_loop(configuration_handler.PROJECTCONFIGURATION.MaxIterations,
            configuration_handler.PROJECTCONFIGURATION.Iteration_Interval_Time,
            )


