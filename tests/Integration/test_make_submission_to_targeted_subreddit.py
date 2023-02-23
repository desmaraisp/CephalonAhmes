from typing import List
import praw.models, os, uuid
from src import (
        ConfigurationHandler as cgf,
        PrawUtilities as pru
)


def test_make_submission_to_targeted_subreddit() -> None:
    praw_settings = cgf.PrawSettings(
        Notify=True,
        PRAW_CLIENT_ID=os.environ["CEPHALONAHMES_PRAW_CLIENT_ID"],
        PRAW_CLIENT_SECRET=os.environ["CEPHALONAHMES_PRAW_CLIENT_SECRET"],
        PRAW_PASSWORD=os.environ["CEPHALONAHMES_PRAW_PASSWORD"],
        PRAW_USERNAME=os.environ["CEPHALONAHMES_PRAW_USERNAME"],
        SubredditDestinationFallbacks=["scrappertest"],
        NotificationDestinationUsername=os.environ["CEPHALONAHMES_PRAW_USERNAME"]
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
    
    corresponding_submissions[0].delete()