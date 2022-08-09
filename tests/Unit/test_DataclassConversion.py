from src import (
        DataclassConversions,
        SubmissionsModels
)


def test_convert_post_history_model_to_json():
    individual_submission_model2 = SubmissionsModels.IndividualSubmissionModel(
            "submission_title2", "submission_url2")

    input_object = SubmissionsModels.SubmissionModelsForAllForumSources([
            SubmissionsModels.SubmissionModelsForSingleForumSource("test", [
                    SubmissionsModels.IndividualSubmissionModel(
                            "submission_title", "submission_url"),
                    individual_submission_model2
            ]),

            SubmissionsModels.SubmissionModelsForSingleForumSource("test2", [
                    individual_submission_model2, individual_submission_model2
            ])
    ])

    output_object = DataclassConversions.convert_post_history_model_to_json(
            input_object)

    expected_object = {
            "forum_sources": [
                    {
                            "submission_source_forum_url": "test",
                            "submissions_list": [
                                    {
                                            "submission_title": "submission_title",
                                            "submission_url": "submission_url"
                                    },
                                    {
                                            "submission_title": "submission_title2",
                                            "submission_url": "submission_url2"}
                            ]
                    },
                    {
                            "submission_source_forum_url": "test2",
                            "submissions_list": [
                                    {
                                            "submission_title": "submission_title2",
                                            "submission_url": "submission_url2"
                                    },
                                    {
                                            "submission_title": "submission_title2",
                                            "submission_url": "submission_url2"
                                    }
                            ]
                    }
            ]
    }

    assert(output_object == expected_object)


def test_convert_post_history_json_to_submission_model():
    input_object = {
            "forum_sources": [
                    {
                            "submission_source_forum_url": "testforumurl1",
                            "submissions_list": [
                                    {
                                            "submission_title": "title_test1",
                                            "submission_url": "submission_url1"
                                    },
                                    {
                                            "submission_title": "title_test2",
                                            "submission_url": "submission_url2"
                                    }
                            ]
                    },
                    {
                            "submission_source_forum_url": "testforumurl2",
                            "submissions_list": [
                                    {
                                            "submission_title": "title_test3",
                                            "submission_url": "submission_url3"
                                    },
                                    {
                                            "submission_title": "title_test4",
                                            "submission_url": "submission_url4"
                                    }
                            ]
                    }
            ]
    }

    output_object = DataclassConversions.convert_post_history_json_to_submission_model(
            input_object)

    expected_object = SubmissionsModels.SubmissionModelsForAllForumSources([
            SubmissionsModels.SubmissionModelsForSingleForumSource("testforumurl1", 
                    [
                            SubmissionsModels.IndividualSubmissionModel(
                                    "title_test1", "submission_url1"),
                            SubmissionsModels.IndividualSubmissionModel(
                                    "title_test2", "submission_url2")
                    ]
            ),

            SubmissionsModels.SubmissionModelsForSingleForumSource("testforumurl2", 
                    [
                            SubmissionsModels.IndividualSubmissionModel(
                                    "title_test3", "submission_url3"),
                            SubmissionsModels.IndividualSubmissionModel(
                                    "title_test4", "submission_url4")
                    ]
            )
    ])

    assert(output_object == expected_object)


def test_convert_dataclass_models_back_and_forth():
    input_object = {
            "forum_sources": [
                    {
                            "submission_source_forum_url": "testforumurl1",
                            "submissions_list": [
                                    {
                                            "submission_title": "title_test1",
                                            "submission_url": "submission_url1"
                                    },
                                    {
                                            "submission_title": "title_test2",
                                            "submission_url": "submission_url2"
                                    }
                            ]
                    },
                    {
                            "submission_source_forum_url": "testforumurl2",
                            "submissions_list": [
                                    {
                                            "submission_title": "title_test3",
                                            "submission_url": "submission_url3"
                                    },
                                    {
                                            "submission_title": "title_test4",
                                            "submission_url": "submission_url4"
                                    }
                            ]
                    }
            ]
    }

    output_object = DataclassConversions.convert_post_history_json_to_submission_model(
            input_object)
    output_object = DataclassConversions.convert_post_history_model_to_json(
            output_object)


    assert(output_object == input_object)
    
    
def test_convert_post_history_json_to_submission_model_negative_test():
    input_object = {
            "forum_sources": [
                    {
                            "submission_source_forum_url": "testforumurl1",
                            "submissions_list": [
                                    {
                                            "submission_title": "title_test1",
                                            "submission_url": "submission_url1"
                                    },
                                    {
                                            "submission_title": "title_test2",
                                            "submission_url": "submission_url2"
                                    }
                            ]
                    },
                    {
                            "submission_source_forum_url": "testforumurl2",
                            "submissions_list": [
                                    {
                                            "submission_title": "title_test3",
                                            "submission_url": "submission_url3"
                                    },
                                    {
                                            "submission_title": "title_test4",
                                            "submission_url": "submission_url4"
                                    }
                            ]
                    }
            ]
    }

    output_object = DataclassConversions.convert_post_history_json_to_submission_model(
            input_object)

    expected_object = SubmissionsModels.SubmissionModelsForAllForumSources([
            SubmissionsModels.SubmissionModelsForSingleForumSource("testforumurl1", 
                    [
                            SubmissionsModels.IndividualSubmissionModel(
                                    "title_test1", "submission_url1"),
                            SubmissionsModels.IndividualSubmissionModel(
                                    "title_test2", "submission_url2")
                    ]
            )
    ])

    assert(output_object != expected_object)