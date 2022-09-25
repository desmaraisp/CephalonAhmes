from pytest import MonkeyPatch
from src import ConfigurationHandler

def test_load_configuration():
    with MonkeyPatch.context() as mp:
        mp.setenv("CEPHALONAHMES_S3_BUCKETNAME", "ROUGE")
        a, b, c = ConfigurationHandler.init_settings("test")
        
        
    assert(a.Notify)
    assert(a.SubredditDestinationFallbacks == ["test","test2"])
    
    assert(b.PostHistoryFullFileName == "testFile")
    assert(b.S3_BucketName == "ROUGE")
    assert(a.PRAW_CLIENT_ID == "OverrideByEnv")