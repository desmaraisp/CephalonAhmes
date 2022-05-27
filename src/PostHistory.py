from src import (
        SubmissionsModels as dtc
)

def commit_post_to_post_history(current_post_history : dtc.SubmissionModelsForAllForumSources, incoming_changes : dtc.SubmissionModelsForSingleForumSource):
    current_forum_source_in_history : dtc.SubmissionModelsForSingleForumSource = current_post_history.find_forum_source_model_by_url(incoming_changes.submission_source_forum_url)	

    if(not current_forum_source_in_history):
        current_post_history.forum_sources.append(incoming_changes)
        return

    if len(current_forum_source_in_history.submissions_list) >= 3:
        current_forum_source_in_history.submissions_list.pop(0)

    current_forum_source_in_history.submissions_list.append(incoming_changes.submissions_list[0])