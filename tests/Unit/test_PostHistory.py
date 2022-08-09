from src import (
                PostHistory,
                SubmissionsModels
        )

def test_commit_post_to_post_history():
    existing_post_history = SubmissionsModels.SubmissionModelsForAllForumSources([
            SubmissionsModels.SubmissionModelsForSingleForumSource("some_random_forum_url", 
                    [
                            SubmissionsModels.IndividualSubmissionModel(
                                    "Test1", "www.google.com")
                    ]
            )
    ])

    incoming_changes = SubmissionsModels.SubmissionModelsForSingleForumSource("some_random_forum_url", 
                    [
                            SubmissionsModels.IndividualSubmissionModel(
                                    "Test2", "https://www.test.com")
                    ]
            )




    PostHistory.commit_post_to_post_history(existing_post_history, incoming_changes)


    expected_post_history = SubmissionsModels.SubmissionModelsForAllForumSources([
            SubmissionsModels.SubmissionModelsForSingleForumSource("some_random_forum_url", 
                    [
                            SubmissionsModels.IndividualSubmissionModel(
                                    "Test1", "www.google.com"),
                            SubmissionsModels.IndividualSubmissionModel(
                                    "Test2", "https://www.test.com"),
                    ]
            )
    ])

    assert existing_post_history == expected_post_history


def test_commit_post_to_post_history_when_max_length_is_reached():
    existing_post_history = SubmissionsModels.SubmissionModelsForAllForumSources([
            SubmissionsModels.SubmissionModelsForSingleForumSource("some_random_forum_url", 
                    [
                            SubmissionsModels.IndividualSubmissionModel(
                                    "Test1", "www.google.com"),
                            SubmissionsModels.IndividualSubmissionModel(
                                    "Test2", "www.google.com"),
                            SubmissionsModels.IndividualSubmissionModel(
                                    "Test3", "www.google.com")
                    ]
            )
    ])

    incoming_changes = SubmissionsModels.SubmissionModelsForSingleForumSource("some_random_forum_url", 
                    [
                            SubmissionsModels.IndividualSubmissionModel(
                                    "Test4", "www.google.com")
                    ]
            )




    PostHistory.commit_post_to_post_history(existing_post_history, incoming_changes)


    expected_post_history = SubmissionsModels.SubmissionModelsForAllForumSources([
            SubmissionsModels.SubmissionModelsForSingleForumSource("some_random_forum_url", 
                    [
                            SubmissionsModels.IndividualSubmissionModel(
                                    "Test2", "www.google.com"),
                            SubmissionsModels.IndividualSubmissionModel(
                                    "Test3", "www.google.com"),
                            SubmissionsModels.IndividualSubmissionModel(
                                    "Test4", "www.google.com"),
                    ]
            )
    ])

    assert existing_post_history == expected_post_history

def test_commit_post_to_post_history_when_first_time_committing():
    existing_post_history = SubmissionsModels.SubmissionModelsForAllForumSources([
            SubmissionsModels.SubmissionModelsForSingleForumSource("some_random_forum_url", 
                    [
                            SubmissionsModels.IndividualSubmissionModel(
                                    "Test1", "www.google.com"),
                            SubmissionsModels.IndividualSubmissionModel(
                                    "Test2", "www.google.com"),
                            SubmissionsModels.IndividualSubmissionModel(
                                    "Test3", "www.google.com")
                    ]
            )
    ])

    incoming_changes = SubmissionsModels.SubmissionModelsForSingleForumSource("a_different_random_forum_url", 
                    [
                            SubmissionsModels.IndividualSubmissionModel(
                                    "Test1", "www.google.com")
                    ]
            )




    PostHistory.commit_post_to_post_history(existing_post_history, incoming_changes)


    expected_post_history = SubmissionsModels.SubmissionModelsForAllForumSources([
            SubmissionsModels.SubmissionModelsForSingleForumSource("some_random_forum_url", 
                    [
                            SubmissionsModels.IndividualSubmissionModel(
                                    "Test1", "www.google.com"),
                            SubmissionsModels.IndividualSubmissionModel(
                                    "Test2", "www.google.com"),
                            SubmissionsModels.IndividualSubmissionModel(
                                    "Test3", "www.google.com"),
                    ]
            ),
            SubmissionsModels.SubmissionModelsForSingleForumSource("a_different_random_forum_url", 
                    [
                            SubmissionsModels.IndividualSubmissionModel(
                                    "Test1", "www.google.com")
                    ]
            ),
    ])

    assert existing_post_history == expected_post_history