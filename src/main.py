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
import logging, os, copy

def main(AWS_Request_ID: Optional[str] = None) -> None:
    try:
        _main(AWS_Request_ID)
    except Exception as e:
        logging.getLogger().exception(e)
        raise


def _main(AWS_Request_ID: Optional[str] = None) -> None:
    ConfigureLogging.ConfigureLogging(AWS_Request_ID)

    logging.getLogger("CephalonAhmes").info("Starting application")
    
    praw_settings, s3_settings, general_settings = cfg.init_settings(os.getenv('ConfigurationName', None))

    praw_utilities : pru.PrawUtilities = pru.PrawUtilities(praw_settings)
    s3_utilities: s3b.S3Utilities = s3b.S3Utilities(s3_settings)
    post_history: dtc.SubmissionListForMultipleSources = s3_utilities.fetch_post_history_from_bucket()
    initial_post_history = copy.deepcopy(post_history)
    
    for XMLUrl in general_settings.XML_Urls:
        response = WebRequestMethods.get_response_from_generic_url(XMLUrl)
        
        if(response.headers.get('expires', '0') != '0'):
            logging.warning(f"Getting cached data from website. Expires at {response.headers['expires']}")
        
        rss_feed_content = response.text
        submission_model = ParsingUtilities.GetLastItemInformation(rss_feed_content)
        
        post_history_for_current_source_rss_feed = next((i for i in post_history.forum_sources if i.rss_source_url == XMLUrl), None)
        
        if post_history_for_current_source_rss_feed and len([i for i in post_history_for_current_source_rss_feed.submissions_list if i.title == submission_model.title or i.guid==submission_model.guid]) > 0:
            continue
        
        if not StringManipulations.get_title_validity(
            submission_model.title,
            general_settings.title_ignore_patterns
        ):
            logging.getLogger("CephalonAhmes").info("Submission Ignored with title {}.".format(submission_model.title))
            post_history.add_submission(submission_model, XMLUrl)
            
        
        submission_contents_markdown = ParsingUtilities.transform_contents_to_markdown(
                        StringManipulations.apply_many_regex_transforms(submission_model.contents, general_settings.body_replace),
                        submission_model.link,
                        general_settings.footer_message
                )

        praw_utilities.make_submission_to_targeted_subreddit(
            submission_contents_markdown,
            StringManipulations.apply_many_regex_transforms(submission_model.title, general_settings.title_replace)
        )
        logging.getLogger("CephalonAhmes").info(f"Submitted post with title {submission_model.title}")
        post_history.add_submission(submission_model, XMLUrl)
    
    if(post_history != initial_post_history):
        s3_utilities.push_post_history_to_bucket(post_history)


if __name__ == "__main__":
    main()
