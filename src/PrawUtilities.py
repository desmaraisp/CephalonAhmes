import praw
from src import (
        ConfigurationHandler as configuration_handler,
        StringManipulations as SMS
)


def start_reddit_session() -> praw.Reddit:
    bot_login = praw.Reddit(
            client_id=configuration_handler.PROJECTCONFIGURATION.PRAW_CLIENT_ID,
            client_secret=configuration_handler.PROJECTCONFIGURATION.PRAW_CLIENT_SECRET,
            user_agent='warframe patch notes retriever bot 0.1',
            username=configuration_handler.PROJECTCONFIGURATION.PRAW_USERNAME,
            password=configuration_handler.PROJECTCONFIGURATION.PRAW_PASSWORD,
            validate_on_submit=True,
            check_for_async=False,
    )
    bot_login.validate_on_submit = True
    return bot_login


def check_if_post_has_already_been_posted_to_subreddit(title: str, subreddit_name: str) -> bool:
    newest_submission_titles_in_subreddit = [
            sub_new_post.title for sub_new_post in start_reddit_session().subreddit(subreddit_name).new(limit=10)]
    return title in newest_submission_titles_in_subreddit


def get_subreddit_flair_id(subreddit_name):
    flair_template = list(start_reddit_session().subreddit(
            subreddit_name).flair.link_templates)
    return next(
            (item.get('id') for item in flair_template if item["text"] == "News"),
            next(
                    (item.get('id')
                     for item in flair_template if item["text"] == "Discussion"),
                    None
            )
    )




def get_destination_subreddit_from_configuration(submission_title):
    if check_if_post_has_already_been_posted_to_subreddit(submission_title,
                configuration_handler.PROJECTCONFIGURATION.PrimaryDestinationSubreddit):
        return configuration_handler.PROJECTCONFIGURATION.SecondaryDestinationSubreddit

    return configuration_handler.PROJECTCONFIGURATION.PrimaryDestinationSubreddit


def make_submission_to_targeted_subreddit(submission_contents, submission_title):
    # Splitting and posting
    bot_login = start_reddit_session()
    DestinationSubreddit = get_destination_subreddit_from_configuration(submission_title)

    news_flair_id = get_subreddit_flair_id(DestinationSubreddit)

    content_before_limit, content_after_limit = SMS.split_string_on_last_separator_before_cutoff_length(
            submission_contents, 40000, ['\n\n', '\n'])

    submission : praw.reddit.Submission = bot_login.subreddit(DestinationSubreddit).submit(
            submission_title, selftext=content_before_limit.strip(), flair_id=news_flair_id, send_replies=False)

    if(configuration_handler.PROJECTCONFIGURATION.Notify):
        bot_login.redditor(configuration_handler.PROJECTCONFIGURATION.BotOwnerUsername).message(
                subject= submission_title, message=submission.url
            )

    while content_after_limit:
        content_before_limit, content_after_limit = SMS.split_string_on_last_separator_before_cutoff_length(
                content_after_limit, 10000, ['\n\n', '\n'])
        submission = submission.reply(body=content_before_limit.strip())
        submission.disable_inbox_replies()

