from src import StringManipulations

def test_Check_Title_Validity() -> None:
    title = "PSA: TestTitle"
    Forum = "Test"

    title, valid = StringManipulations.Check_Title_Validity(title, Forum)
    assert title == "TestTitle"
    assert(valid)

    title = "Update1+Hotfix1.1"
    Forum = "https://forums.warframe.com/forum/3-pc-update-notes.xml"

    title, valid = StringManipulations.Check_Title_Validity(title, Forum)
    assert not valid



def test_split_string_on_last_separator_before_cutoff_length() -> None:
    content = "TestParagraph1"
    result = StringManipulations.split_string_on_last_separator_before_cutoff_length(content, 15, [","])

    assert result == ("TestParagraph1","")


    content = "TestParagraph1,TestParagraph2,TestParagraph3"
    result = StringManipulations.split_string_on_last_separator_before_cutoff_length(content, 15, [","])

    assert result == ("TestParagraph1","TestParagraph2,TestParagraph3")


    content = "TestParagraph1.TestParagraph2,TestParagraph3"
    result = StringManipulations.split_string_on_last_separator_before_cutoff_length(content, 15, [",","."])

    assert result == ("TestParagraph1","TestParagraph2,TestParagraph3")

    content = "TestParagraph1"
    result = StringManipulations.split_string_on_last_separator_before_cutoff_length(content, 4)

    assert result == ("Test","Paragraph1")