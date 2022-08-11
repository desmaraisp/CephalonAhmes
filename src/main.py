import src.SleepHandler
from src import (
        DataclassConversions,
        HTMLCorrections as HTML_Corrections,
        ExitHandler,
        S3BucketFunctions as s3b,
        ConfigurationHandler as configuration_handler,
        SeleniumUtilities,
        SubmissionsModels as dtc,
        WebRequestMethods,
        ParsingUtilities,
        PrawUtilities,
        StringManipulations,
        PostHistory
)
import typing, logging.config, html, time
import html2text as htt
from bs4 import BeautifulSoup
import dpath.util as dpu
from selenium import webdriver




def get_and_parse_notes_from_response_contents(ResponseContent, url: str, SubmissionTitle: str, ForumSourceURL):
    ResponseContent = StringManipulations.remove_all_zero_width_spaces(ResponseContent)

    soup = BeautifulSoup(ResponseContent, 'html.parser')
    main_post_tag = ParsingUtilities.get_post_element_from_full_discussion(soup)
    post_contents_HTML = HTML_Corrections.get_post_contents_from_post_tag(soup, main_post_tag)

    htt_conf = htt.HTML2Text()
    htt_conf.use_automatic_links = True
    htt_conf.body_width = 0

    post_contents = htt_conf.handle(post_contents_HTML.decode_contents())
    # Because Reddit's implementation of markdown does not support inline links like this: ![]()
    post_contents = post_contents.replace("![", '[')
    post_contents = html.unescape(post_contents)

    SubmissionTitle, SubmissionValidTitle = StringManipulations.Check_Title_Validity(
            SubmissionTitle, ForumSourceURL)
    if not SubmissionValidTitle:
        logging.getLogger().warning("Submission Ignored with title {}.".format(SubmissionTitle))
        return None, None

    automatic_message = "\n------\n^(This action was performed automatically, if you see any mistakes, please tag u/{}, he'll fix them.) [^(Here is my github)](https://github.com/CephalonAhmes/CephalonAhmes)".format(
            configuration_handler.PROJECTCONFIGURATION.BotOwnerUsername)
    post_contents = "[Source]({})\n\n{}{}".format(
            url, post_contents, automatic_message)

    return post_contents, SubmissionTitle







def fetch_and_parse_forum_pages_and_return_latest_posts_for_all_sources(forums_url_list: typing.List[str], browser: webdriver.Chrome) -> dtc.SubmissionModelsForAllForumSources:
    newest_posts_on_warframe_forum = dtc.SubmissionModelsForAllForumSources()
    for forum_url in forums_url_list:
        page_source = WebRequestMethods.browser_fetch_updated_forum_page_source(forum_url, browser)
        latest_forum_post: dtc.IndividualSubmissionModel = ParsingUtilities.get_latest_submission_dataclass_in_forum_page(
                page_source)

        newest_posts_on_warframe_forum.forum_sources.append(dtc.SubmissionModelsForSingleForumSource(forum_url, [latest_forum_post]))
    return newest_posts_on_warframe_forum


def main_loop(MaxIterations, Iteration_Interval_Time):
    """
    Parameters
    ----------
    Get_Posts_From_General_Discussions_Page : bool
                    Whether the posted notes will be pulled from the intended forum pages (news, updates, etc) or from the general discussions page. Set to False for the news pages and True for General Discussions.
    Post_To_scrappertest_subreddit : bool
                    Whether the posted notes will be posted in the scrappertest subreddit by default. Set to False to post to r/warframe or True scrappertest.
    """

    browser: webdriver.Chrome = SeleniumUtilities.start_chrome_browser()

    post_history: dtc.SubmissionModelsForAllForumSources = s3b.fetch_post_history_from_bucket()
    logging.config.fileConfig(
            configuration_handler.PROJECTCONFIGURATION.LoggingConfigFileName)

    Exit_Handler = ExitHandler.ExitHandlerClass(
            browser, post_history)
    CurrentIteration = 0

    while CurrentIteration != MaxIterations:
        newest_posts_on_warframe_forum: dtc.SubmissionModelsForAllForumSources = fetch_and_parse_forum_pages_and_return_latest_posts_for_all_sources(
                configuration_handler.PROJECTCONFIGURATION.forum_urls_list,
                browser
                )

        for forum_source in newest_posts_on_warframe_forum.forum_sources:
            latest_forum_post_for_current_forum_source = forum_source.submissions_list[0]

            condition1 = latest_forum_post_for_current_forum_source.submission_url not in dpu.values(
                    DataclassConversions.convert_post_history_model_to_json(post_history),
                    'forum_sources/*/submissions_list/*/submission_url'
            )
            condition2 = latest_forum_post_for_current_forum_source.submission_title not in dpu.values(
                    DataclassConversions.convert_post_history_model_to_json(post_history),
                    'forum_sources/*/submissions_list/*/submission_title'
            )

            if condition1 and condition2:
                response_contents = WebRequestMethods.get_response_text_from_generic_url(
                        latest_forum_post_for_current_forum_source.submission_url)

                submission_contents, submission_title = get_and_parse_notes_from_response_contents(
                        response_contents, latest_forum_post_for_current_forum_source.submission_url, latest_forum_post_for_current_forum_source.submission_title,forum_source.submission_source_forum_url)

                Exit_Handler.enable_lock()
                if(submission_contents):
                    PrawUtilities.make_submission_to_targeted_subreddit(
                            submission_contents, submission_title)

                logging.getLogger().warning(latest_forum_post_for_current_forum_source.submission_title)
                PostHistory.commit_post_to_post_history(post_history, forum_source)
                Exit_Handler.disable_lock()

        time.sleep(Iteration_Interval_Time)
        CurrentIteration += 1


if __name__ == "__main__":
    main_loop(configuration_handler.PROJECTCONFIGURATION.MaxIterations,
                      configuration_handler.PROJECTCONFIGURATION.Iteration_Interval_Time,
                      )
