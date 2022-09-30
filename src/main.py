from typing import Optional
from src import (
        ConfigurationHandler as cfg,
        Models as dtc,
        S3Utilities as s3b,
        WebRequestMethods,
        ParsingUtilities,
        PrawUtilities as pru,
        StringManipulations,
        ConfigureLogging
)
import logging, os

def main(AWS_Request_ID: Optional[str] = None):
    try:
        _main(AWS_Request_ID)
    except Exception as e:
        logging.getLogger().exception(e)
        raise


def _main(AWS_Request_ID: Optional[str] = None):
    ConfigureLogging.ConfigureLogging(AWS_Request_ID)

    logging.getLogger("CephalonAhmes").info("Starting application")
    
    praw_settings, s3_settings, general_settings = cfg.init_settings(os.getenv('ConfigurationName', None))

    praw_utilities : pru.PrawUtilities = pru.PrawUtilities(praw_settings)
    s3_utilities: s3b.S3Utilities = s3b.S3Utilities(s3_settings)
    post_history: dtc.SubmissionListForMultipleSources = s3_utilities.fetch_post_history_from_bucket()
    
    rss_feed_information: cfg.RSSFeedInformation
    for rss_feed_information in general_settings.forum_urls_list:
        if rss_feed_information.RefreshUrl:
            _ = WebRequestMethods.get_response_from_generic_url(rss_feed_information.RefreshUrl)
        
        rss_feed_content = WebRequestMethods.get_response_from_generic_url(rss_feed_information.XMLUrl).text
        submission_model = ParsingUtilities.GetLastItemInformation(rss_feed_content)
        
        post_history_for_current_source_rss_feed = next((i for i in post_history.forum_sources if i.rss_source_url == rss_feed_information.XMLUrl), None)
        
        if post_history_for_current_source_rss_feed and len([i for i in post_history_for_current_source_rss_feed.submissions_list if i.title == submission_model.title or i.guid==submission_model.guid]) == 1:
            continue
        
        submission_model.title, SubmissionValidTitle = StringManipulations.Check_Title_Validity(
            submission_model.title,
            rss_feed_information.XMLUrl
        )
        
        if not SubmissionValidTitle:
            logging.getLogger("CephalonAhmes").info("Submission Ignored with title {}.".format(submission_model.title))
            post_history.add_submission(submission_model, rss_feed_information.XMLUrl)
            
        
        submission_contents_markdown = ParsingUtilities.transform_contents_to_markdown(
                        submission_model.contents,
                        submission_model.link,
                        general_settings.footer_message
                )

        praw_utilities.make_submission_to_targeted_subreddit(
            submission_contents_markdown, submission_model.title)
        logging.getLogger("CephalonAhmes").info(f"Submitted post with title {submission_model.title}")
        post_history.add_submission(submission_model, rss_feed_information.XMLUrl)
    
    s3_utilities.push_post_history_to_bucket(post_history)


if __name__ == "__main__":
    main()
