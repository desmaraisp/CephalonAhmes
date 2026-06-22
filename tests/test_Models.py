from src import Models

def test_add_submission() -> None:
    model = Models.SubmissionListForMultipleSources(
        forum_sources=[
            Models.SubmissionsListForSingleSource(
                rss_source_url="Url1",
                submissions_list=[
                    Models.SubmissionModel(title="test1")
                ]
            )
        ]
    )

    model.add_submission(Models.SubmissionModel(title="test2"), "Url1")

    assert(len(model.forum_sources[0].submissions_list) == 2)

    model.add_submission(Models.SubmissionModel(title="test3"), "Url2")

    assert(len(model.forum_sources) == 2)

    model.add_submission(Models.SubmissionModel(title="test2"), "Url1")
    model.add_submission(Models.SubmissionModel(title="test2"), "Url1")
    assert(len(model.forum_sources[0].submissions_list) == 3)
    assert(model.forum_sources[0].submissions_list[0].title != "test1")
