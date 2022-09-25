from dataclasses import dataclass
from typing import List, Dict
import pytest, pytest_mock
from src import (
        ConfigurationHandler as cgf,
        StringManipulations as SMS,
        PrawUtilities as pru
)

@dataclass
class mocked_submission_class:
    title: str

@dataclass
class mocked_subreddit_object:
    return_value: List[mocked_submission_class]

    def new(self, limit:int):
        return self.return_value

@dataclass
class mocked_Reddit_Object:
    subreddit_return_value: Dict[str, mocked_subreddit_object]
    
    def subreddit(self, name: str):
        return self.subreddit_return_value[name]
    
@pytest.fixture
def mock_praw(mocker: pytest_mock.MockerFixture):
    mock_function = mocker.patch.object(pru.PrawUtilities, 'start_reddit_session')
    mock_function.return_value = mocked_Reddit_Object({
        "sub1": mocked_subreddit_object(
            return_value= [
                        mocked_submission_class(title="test"),
                        mocked_submission_class(title="test2")
                    ]
        ),
        "sub2": mocked_subreddit_object(
            return_value= [
                        mocked_submission_class(title="test3"),
                        mocked_submission_class(title="test4")
                    ]
        )
    })
    
    yield mock_function

def test_check_if_post_has_already_been_posted_to_subreddit(mock_praw):
    praw_utilities: pru.PrawUtilities = pru.PrawUtilities(
        cgf.PrawSettings(
            Notify=False,
            PRAW_CLIENT_ID="",
            PRAW_CLIENT_SECRET="",
            PRAW_PASSWORD="",
            PRAW_USERNAME="",
            SubredditDestinationFallbacks=[]
        )
    )
    
    result: bool = praw_utilities.check_if_post_has_already_been_posted_to_subreddit("test", "sub1")
    result2: bool = praw_utilities.check_if_post_has_already_been_posted_to_subreddit("test2", "sub1")
    result3: bool = praw_utilities.check_if_post_has_already_been_posted_to_subreddit("test3","sub1")
    result4: bool = praw_utilities.check_if_post_has_already_been_posted_to_subreddit("test3","sub2")
    assert(result)
    assert(result2)
    assert(not result3)
    assert(result4)


def test_get_destination_subreddit_from_configuration(mock_praw):
    praw_utilities: pru.PrawUtilities = pru.PrawUtilities(
        cgf.PrawSettings(
            Notify=False,
            PRAW_CLIENT_ID="",
            PRAW_CLIENT_SECRET="",
            PRAW_PASSWORD="",
            PRAW_USERNAME="",
            SubredditDestinationFallbacks=["sub1", "sub2"]
        )
    )
    
    result: str = praw_utilities.get_destination_subreddit_from_configuration("test")
    assert(result=="sub1")
    result: str = praw_utilities.get_destination_subreddit_from_configuration("test3")
    assert(result=="sub2")
    result: str = praw_utilities.get_destination_subreddit_from_configuration("test5")
    assert(result=="sub2")

