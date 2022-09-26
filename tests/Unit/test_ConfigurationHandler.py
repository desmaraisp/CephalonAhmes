from pytest import MonkeyPatch
from requests import delete
from src import ConfigurationHandler

def test_load_configuration():
    with MonkeyPatch.context() as mp:
        mp.setenv("CEPHALONAHMES_S3_BUCKETNAME", "ROUGE")
        mp.delenv("CEPHALONAHMES_PRAW_CLIENT_ID", False)
        a, b, c = ConfigurationHandler.init_settings("test")
        
        
    assert(a.Notify)
    assert(a.SubredditDestinationFallbacks == ["test","test2"])
    
    assert(b.PostHistoryFullFileName == "testFile")
    assert(b.S3_BucketName == "ROUGE")
    assert(a.PRAW_CLIENT_ID == "OverrideByEnv")