from pytest import MonkeyPatch
import pytest
from typed_settings import exceptions
from src import ConfigurationHandler

def test_load_configuration() -> None:
    with MonkeyPatch.context() as mp:
        mp.setenv("CEPHALONAHMES_S3_BUCKETNAME", "ROUGE")
        mp.delenv("CEPHALONAHMES_PRAW_CLIENT_ID", False)
        a, b, c = ConfigurationHandler.init_settings("test")
        
        
    assert(a.Notify)
    assert(a.SubredditDestinationFallbacks == ["test","test2"])
    
    assert(b.PostHistoryFullFileName == "testFile")
    assert(b.S3_BucketName == "ROUGE")
    assert(a.PRAW_CLIENT_ID == "OverrideByEnv")
    assert(len(c.XML_Urls) == 2)
    assert(c.title_ignore_patterns == [r'(?i)(hotfix|update).*\+|\+.*(hotfix|update)'])
    assert(len(c.title_replace) == 2)

def test_load_configuration_invalid_values() -> None:
    with MonkeyPatch.context() as mp:
        mp.setenv("CEPHALONAHMES_S3_BUCKETNAME", "")
        with pytest.raises(exceptions.InvalidValueError):
            ConfigurationHandler.init_settings("test")