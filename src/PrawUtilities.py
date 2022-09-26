import praw, praw.models
from src import (
        ConfigurationHandler as cgf,
        StringManipulations as SMS
)

class PrawUtilities:
    settings : cgf.PrawSettings
    
    def __init__(self, settings : cgf.PrawSettings):
        self.settings = settings

    def start_reddit_session(self) -> praw.Reddit:
        bot_login = praw.Reddit(
                client_id=self.settings.PRAW_CLIENT_ID,
                client_secret=self.settings.PRAW_CLIENT_SECRET,
                user_agent='warframe patch notes retriever bot 0.1',
                username=self.settings.PRAW_USERNAME,
                password=self.settings.PRAW_PASSWORD,
                validate_on_submit=True,
                check_for_async=False,
        )
        bot_login.validate_on_submit = True
        return bot_login


    def check_if_post_has_already_been_posted_to_subreddit(self, title: str, subreddit_name: str) -> bool:
        newest_submission_titles_in_subreddit = [
                sub_new_post.title for sub_new_post in self.start_reddit_session().subreddit(subreddit_name).new(limit=10)]
        return title in newest_submission_titles_in_subreddit


    def get_subreddit_flair_id(self, subreddit_name):
        flair_template = list(self.start_reddit_session().subreddit(
                subreddit_name).flair.link_templates)
        return next(
                (item.get('id') for item in flair_template if item["text"] == "News"),
                next(
                        (item.get('id')
                        for item in flair_template if item["text"] == "Discussion"),
                        None
                )
        )


    def get_destination_subreddit_from_configuration(self, submission_title: str) -> str:
        for subreddit in self.settings.SubredditDestinationFallbacks:
            has_been_posted: bool = self.check_if_post_has_already_been_posted_to_subreddit(
                    submission_title,
                    subreddit
                )
            if(has_been_posted): return subreddit
        
        return self.settings.SubredditDestinationFallbacks[-1]


    def make_submission_to_targeted_subreddit(self, submission_contents: str, submission_title: str) -> None:
        # Splitting and posting
        bot_login = self.start_reddit_session()
        DestinationSubreddit = self.get_destination_subreddit_from_configuration(submission_title)

        news_flair_id = self.get_subreddit_flair_id(DestinationSubreddit)

        content_before_limit, content_after_limit = SMS.split_string_on_last_separator_before_cutoff_length(
                submission_contents, 40000, ['\n\n', '\n'])

        submission : praw.models.Submission = bot_login.subreddit(DestinationSubreddit).submit(
                submission_title,
                selftext=content_before_limit.strip(),
                flair_id=news_flair_id,
                send_replies=False
        )

        if(self.settings.Notify):
            bot_login.redditor(self.settings.NotificationDestinationUsername).message(
                    subject= submission_title, message=submission.url
                )

        while content_after_limit:
            content_before_limit, content_after_limit = SMS.split_string_on_last_separator_before_cutoff_length(
                    content_after_limit, 10000, ['\n\n', '\n'])
            submission = submission.reply(body=content_before_limit.strip())
            submission.disable_inbox_replies()

