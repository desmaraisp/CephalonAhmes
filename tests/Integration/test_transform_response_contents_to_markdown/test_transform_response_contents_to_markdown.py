from src import (
    ParsingUtilities
    )
import pytest


@pytest.mark.integtest
def test_transform_response_contents_to_markdown():
    with open("tests/Integration/test_transform_response_contents_to_markdown/source_for_test_Get_and_Parse_Notes.html") as file:
        contents = file.read().replace("\t", "").replace("\n", "")

    with open("tests/Integration/test_transform_response_contents_to_markdown/Expected_for_test_Get_and_Parse_Notes.md") as file:
        Expected = file.read()

    Result = ParsingUtilities.transform_response_contents_to_markdown(contents, "https://test.com", "Footer")

    assert Result == Expected
