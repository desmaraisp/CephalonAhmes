from dataclasses import dataclass
from typing import List, Dict
import pytest, pytest_mock, unittest.mock
from src import (
        ConfigurationHandler as cgf,
        PrawUtilities as pru
)

@dataclass
class mocked_submission_class:
    title: str

@dataclass
class mocked_subreddit_object:
    return_value: List[mocked_submission_class]

    def new(self, limit:int) -> List[mocked_submission_class]:
        return self.return_value

@dataclass
class mocked_Reddit_Object:
    subreddit_return_value: Dict[str, mocked_subreddit_object]
    
    def subreddit(self, name: str) -> mocked_subreddit_object:
        return self.subreddit_return_value[name]
    
@pytest.fixture
def mock_praw(mocker: pytest_mock.MockerFixture) -> unittest.mock.MagicMock:
    mock_function = mocker.patch.object(pru.PrawUtilities, 'start_reddit_session')
    mock_function.return_value = mocked_Reddit_Object({
        "primary": mocked_subreddit_object(
            return_value= [
                        mocked_submission_class(title="test"),
                        mocked_submission_class(title="test2")
                    ]
        ),
        "fallback": mocked_subreddit_object(
            return_value= [
                        mocked_submission_class(title="test2"),
                        mocked_submission_class(title="test3")
                    ]
        )
    })
    
    return mock_function

def test_check_if_post_has_already_been_posted_to_subreddit(mock_praw: unittest.mock.MagicMock, mocker: pytest_mock.MockerFixture) -> None:
    mocker.patch('src.ConfigurationHandler.ThrowValidationException', return_value=None)

    praw_utilities: pru.PrawUtilities = pru.PrawUtilities(
        cgf.PrawSettings()
    )
    
    result: bool = praw_utilities.check_if_post_has_already_been_posted_to_subreddit("test", "primary")
    result2: bool = praw_utilities.check_if_post_has_already_been_posted_to_subreddit("test2", "primary")
    result3: bool = praw_utilities.check_if_post_has_already_been_posted_to_subreddit("test3","primary")
    result4: bool = praw_utilities.check_if_post_has_already_been_posted_to_subreddit("test3","fallback")
    assert(result)
    assert(result2)
    assert(not result3)
    assert(result4)


def test_get_destination_subreddit_from_configuration(mock_praw: unittest.mock.MagicMock, mocker: pytest_mock.MockerFixture) -> None:
    mocker.patch('src.ConfigurationHandler.ThrowValidationException', return_value=None)
    
    praw_utilities: pru.PrawUtilities = pru.PrawUtilities(
        cgf.PrawSettings(
            SubredditDestinationFallbacks=["primary", "fallback"]
        )
    )
    
    result: str = praw_utilities.get_destination_subreddit_from_configuration("test")
    assert(result=="fallback")
    result = praw_utilities.get_destination_subreddit_from_configuration("test3")
    assert(result=="primary")
    result = praw_utilities.get_destination_subreddit_from_configuration("test2")
    assert(result=="fallback")