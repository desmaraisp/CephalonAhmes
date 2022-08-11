from src import (
    PrawUtilities,
    main as wpts
    )
import pytest

@pytest.mark.integtest
def test_Get_and_Parse_Notes():
    with open("tests/Integration/source_for_test_Get_and_Parse_Notes.html") as file:
        contents = file.read().replace("\t","").replace("\n","")

    with open("tests/Integration/Expected_for_test_Get_and_Parse_Notes.md") as file:
        Expected = file.read()

    Result = wpts.get_and_parse_notes_from_response_contents(contents, "https://test.com", "TitleTest", "ForumSource")

    assert Result[0] == Expected


@pytest.mark.integtest
def test_Pull_Parse_and_Post_Notes():
    with open("tests/Integration/Source_For_Post_Notes.html", encoding='utf-8') as file:
        response_contents = file.read()

    submission_contents, submission_title = wpts.get_and_parse_notes_from_response_contents(
            response_contents, "https://www.testurl.com", "submissiontitle" , "https://forumsource.com")

    if(submission_contents):
        PrawUtilities.make_submission_to_targeted_subreddit(
                submission_contents, submission_title)

