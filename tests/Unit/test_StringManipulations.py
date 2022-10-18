from src import StringManipulations
from src import ConfigurationHandler

def test_get_title_validity_valid() -> None:
    title = "TestTitle"

    valid = StringManipulations.get_title_validity(title, [r'SomeRandomPatter'])
    assert(valid)

def test_get_title_validity_invalid() -> None:
    title = "Update1+Hotfix1.1"

    valid = StringManipulations.get_title_validity(title, [r'(?i)(hotfix|update).*\+|\+.*(hotfix|update)'])
    assert(not valid)
    
def test_get_title_validity_invalid_multiple() -> None:
    title = "Update1+Hotfix1.1"

    valid = StringManipulations.get_title_validity(title, ["some random regex", r'(?i)(hotfix|update).*\+|\+.*(hotfix|update)'])
    assert(not valid)
    
    
def test_apply_many_regex_transforms() -> None:
    text = "Word1, Word2"

    output = StringManipulations.apply_many_regex_transforms(text, [
        ConfigurationHandler.RegexSubstitutionPair(
            pattern='Word1',substitution='NotWord1'
        ),
        ConfigurationHandler.RegexSubstitutionPair(
            pattern='Word2',substitution='NotWord2'
        )
    ])
    assert(output=='NotWord1, NotWord2')


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