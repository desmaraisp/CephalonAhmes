from src import (
        DataclassConversions,
        ConfigurationHandler as configuration_handler,
        S3Utilities as s3b,
        SubmissionsModels as dtc,
        WebRequestMethods,
        ParsingUtilities,
        PrawUtilities as pru,
        StringManipulations,
        PostHistory
)
import typing, logging, os
import dpath.util as dpu



def fetch_and_parse_forum_pages_and_return_latest_posts_for_all_sources(forums_url_list: typing.List[str]) -> dtc.SubmissionModelsForAllForumSources:
    newest_posts_on_warframe_forum = dtc.SubmissionModelsForAllForumSources()
    for forum_url in forums_url_list:
        page_source = WebRequestMethods.get_response_from_generic_url(forum_url)
        print(page_source.text)
        latest_forum_post: dtc.IndividualSubmissionModel = ParsingUtilities.get_latest_submission_dataclass_in_forum_page(
                page_source.text)

        newest_posts_on_warframe_forum.forum_sources.append(dtc.SubmissionModelsForSingleForumSource(forum_url, [latest_forum_post]))
    return newest_posts_on_warframe_forum


def main():
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().info("Starting application")
    
    praw_settings, s3_settings, general_settings = configuration_handler.init_settings(os.getenv('ConfigurationName'))

    praw_utilities : pru.PrawUtilities = pru.PrawUtilities(praw_settings)
    s3_utilities: s3b.S3Utilities = s3b.S3Utilities(s3_settings)
    post_history: dtc.SubmissionModelsForAllForumSources = s3_utilities.fetch_post_history_from_bucket()

    newest_posts_on_warframe_forum: dtc.SubmissionModelsForAllForumSources = fetch_and_parse_forum_pages_and_return_latest_posts_for_all_sources(
            general_settings.forum_urls_list,
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
            response_contents = (WebRequestMethods.get_response_from_generic_url(
                    latest_forum_post_for_current_forum_source.submission_url)).text

            SubmissionTitle, SubmissionValidTitle = StringManipulations.Check_Title_Validity(
                latest_forum_post_for_current_forum_source.submission_title,
                latest_forum_post_for_current_forum_source.submission_url
            )
            if not SubmissionValidTitle:
                logging.getLogger().warning("Submission Ignored with title {}.".format(SubmissionTitle))

            else:
                submission_contents = ParsingUtilities.transform_response_contents_to_markdown(
                        response_contents,
                        latest_forum_post_for_current_forum_source.submission_url,
                        general_settings.footer_message
                )

                praw_utilities.make_submission_to_targeted_subreddit(
                    submission_contents, SubmissionTitle)
                logging.getLogger().warning(SubmissionTitle)

                
            PostHistory.commit_post_to_post_history(post_history, forum_source)
            s3_utilities.push_post_history_to_bucket(post_history)


if __name__ == "__main__":
    main()
