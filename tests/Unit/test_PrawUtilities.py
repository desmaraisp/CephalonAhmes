from dataclasses import dataclass
from typing import List, Dict
import pytest, pytest_mock, praw.models, os, uuid, typed_settings
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

def test_check_if_post_has_already_been_posted_to_subreddit(mock_praw, mocker):
    mocker.patch('src.ConfigurationHandler.ThrowValidationException', return_value=None)

    praw_utilities: pru.PrawUtilities = pru.PrawUtilities(
        cgf.PrawSettings()
    )
    
    result: bool = praw_utilities.check_if_post_has_already_been_posted_to_subreddit("test", "sub1")
    result2: bool = praw_utilities.check_if_post_has_already_been_posted_to_subreddit("test2", "sub1")
    result3: bool = praw_utilities.check_if_post_has_already_been_posted_to_subreddit("test3","sub1")
    result4: bool = praw_utilities.check_if_post_has_already_been_posted_to_subreddit("test3","sub2")
    assert(result)
    assert(result2)
    assert(not result3)
    assert(result4)


def test_get_destination_subreddit_from_configuration(mock_praw, mocker):
    mocker.patch('src.ConfigurationHandler.ThrowValidationException', return_value=None)
    
    praw_utilities: pru.PrawUtilities = pru.PrawUtilities(
        cgf.PrawSettings(
            SubredditDestinationFallbacks=["sub1", "sub2"]
        )
    )
    
    result: str = praw_utilities.get_destination_subreddit_from_configuration("test")
    assert(result=="sub1")
    result: str = praw_utilities.get_destination_subreddit_from_configuration("test3")
    assert(result=="sub2")
    result: str = praw_utilities.get_destination_subreddit_from_configuration("test5")
    assert(result=="sub2")


def test_make_submission_to_targeted_subreddit():
    praw_settings = cgf.PrawSettings(
        Notify=True,
        PRAW_CLIENT_ID=os.environ["PRAW_CLIENT_ID"],
        PRAW_CLIENT_SECRET=os.environ["PRAW_CLIENT_SECRET"],
        PRAW_PASSWORD=os.environ["PRAW_PASSWORD"],
        PRAW_USERNAME=os.environ["PRAW_USERNAME"],
        SubredditDestinationFallbacks=["scrappertest"],
        NotificationDestinationUsername=os.environ["PRAW_USERNAME"]
    )
    praw_utilities: pru.PrawUtilities = pru.PrawUtilities(praw_settings)

    subject = "test-submission-"+ str(uuid.uuid4())

    praw_utilities.make_submission_to_targeted_subreddit(
        submission_contents="a"*35000 + "\n\n" + "a"*9000,
        submission_title=subject
    )

    session = praw_utilities.start_reddit_session()

    messages: List[praw.models.Message] = session.inbox.messages(limit=5)

    corresponding_messages = [message for message in messages if message.subject == subject]

    assert(len(corresponding_messages) != 0)
    session.inbox.mark_read(corresponding_messages)

    submissions: List[praw.models.Submission] = session.subreddit("scrappertest").new(limit=5)
    corresponding_submissions = [submission for submission in submissions if submission.title == subject]

    assert(len(corresponding_submissions) == 1)
    assert(len(corresponding_submissions[0].selftext) == 35000)
    assert(corresponding_submissions[0].num_comments > 0)