import pytest
from src import (
        DataclassConversions,
        Models
)
from datetime import datetime

@pytest.fixture
def shared_class_object():
    individual_submission_model2 = Models.SubmissionModel(
        contents="contents",
        guid=12,
        link="link",
        pub_date=datetime(year=20,month=2,day=2),
        title="title"
    )

    class_object = Models.SubmissionListForMultipleSources(
        forum_sources=[
            Models.SubmissionsListForSingleSource(
                rss_source_url="test", 
                submissions_list=[
                    Models.SubmissionModel(
                        title="submission_title",
                        link="submission_url",
                        guid=123,
                        contents="contents2",
                        pub_date=datetime(year=202,month=5,day=6)
                    ),
                    individual_submission_model2
                ]
            ),

            Models.SubmissionsListForSingleSource(
                "test2",
                [
                    individual_submission_model2, individual_submission_model2
                ]
            )
        ]
    )

    return class_object

@pytest.fixture
def shared_dict_object():
    return {
        "forum_sources": [
                {
                        "rss_source_url": "test",
                        "submissions_list": [
                            {
                                "title":"submission_title",
                                "contents":"contents2",
                                "pub_date":"0202-05-06T00:00:00",
                                "guid":123,
                                "link":"submission_url"
                            },
                            {
                                "title":"title",
                                "contents":"contents",
                                "pub_date":"0020-02-02T00:00:00",
                                "guid":12,
                                "link":"link"
                            }
                        ]
                },
                {
                        "rss_source_url": "test2",
                        "submissions_list": [
                            {
                                "title":"title",
                                "contents":"contents",
                                "pub_date":"0020-02-02T00:00:00",
                                "guid":12,
                                "link":"link"
                            },
                            {
                                "title":"title",
                                "contents":"contents",
                                "pub_date":"0020-02-02T00:00:00",
                                "guid":12,
                                "link":"link"
                            }
                        ]
                }
        ]
    }


def test_convert_post_history_model_to_json_bakc_and_forth(shared_dict_object, shared_class_object):
    assert(shared_dict_object == DataclassConversions.convert_post_history_model_to_json(shared_class_object))
    assert(shared_class_object == DataclassConversions.convert_post_history_json_to_submission_model(shared_dict_object))


def test_convert_post_history_json_to_submission_model_negative_test(shared_class_object, shared_dict_object):
    shared_class_object.forum_sources[0].rss_source_url="ChangeValue"

    output_object = DataclassConversions.convert_post_history_model_to_json(
            shared_class_object)

    assert(output_object != shared_dict_object)
    
    
    
def test_convert_post_history_json_to_submission_model_empty_string():
    input_object = {}

    output_object = DataclassConversions.convert_post_history_json_to_submission_model(input_object)

    expected_object = Models.SubmissionListForMultipleSources()

    assert(output_object == expected_object)