import src.Warframe_patchnotes_thief_script as wpts
import pytest

@pytest.mark.integtest
def test_Get_and_Parse_Notes():
	with open("tests/Integration/source_for_test_Get_and_Parse_Notes.html") as file:
		contents = file.read().replace("\t","").replace("\n","")
	
	with open("tests/Integration/Expected_for_test_Get_and_Parse_Notes.html") as file:
		Expected = file.read()
	
	Result = wpts.Get_and_Parse_Notes(contents, "https://test.com", "TitleTest", "ForumSource")

	assert Result[0] == Expected
	