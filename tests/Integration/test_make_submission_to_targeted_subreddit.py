from typing import List
import praw.models, os, uuid, praw
from src import (
        ConfigurationHandler as cgf,
        PrawUtilities as pru
)


def test_make_submission_to_targeted_subreddit() -> None:
    praw_settings = cgf.PrawSettings(
        Notify=False,
        PRAW_CLIENT_ID=os.environ["CEPHALONAHMES_PRAW_CLIENT_ID"],
        PRAW_CLIENT_SECRET=os.environ["CEPHALONAHMES_PRAW_CLIENT_SECRET"],
        PRAW_PASSWORD=os.environ["CEPHALONAHMES_PRAW_PASSWORD"],
        PRAW_USERNAME=os.environ["CEPHALONAHMES_PRAW_USERNAME"],
        SubredditDestinationFallbacks=["scrappertest"],
        NotificationDestinationUsername="placeholder"
    )
    praw_utilities: pru.PrawUtilities = pru.PrawUtilities(praw_settings)

    generated_uuid: str = str(uuid.uuid4())
    subject = "test-submission-"+ generated_uuid 

    praw_utilities.make_submission_to_targeted_subreddit(
        submission_contents="a"*35000 + "\n\n" + "a"*9000 + generated_uuid,
        submission_title=subject
    )

    session = praw_utilities.start_reddit_session()
    redditor: praw.models.Redditor = session.redditor(os.environ["CEPHALONAHMES_PRAW_USERNAME"])
    submissions: List[praw.models.Submission] = redditor.submissions.new(limit=5)
    corresponding_submissions = [submission for submission in submissions if submission.title == subject]

    assert(len(corresponding_submissions) == 1)
    assert(len(corresponding_submissions[0].selftext) == 35000)
    assert(corresponding_submissions[0].num_comments > 0)
    
    for comment in redditor.comments.new(limit=5):
        if comment.body == "a"*9000 + generated_uuid:
            comment.delete()
    
    corresponding_submissions[0].delete()