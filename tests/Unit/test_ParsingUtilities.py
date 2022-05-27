import src.ParsingUtilities



def test_parse_forum_page_to_pull_latest_posts():
    with open("tests/Unit/source_for_test_parse_forum_page_to_pull_latest_posts.html") as file:
        contents = file.read()

    individual_submission_model = src.ParsingUtilities.get_latest_submission_dataclass_in_forum_page(contents)
    assert individual_submission_model.submission_url=="https://forums.warframe.com/topic/1293591-the-new-war-hotfix-3105/"
    assert individual_submission_model.submission_title == "The New War: Hotfix 31.0.5"	