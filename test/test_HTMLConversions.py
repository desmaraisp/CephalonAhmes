import Warframe_patchnotes_thief_script as wpts




def test_add_multiline_spoiler_tag_if_multiple_line_returns_in_a_row():
	Initial_String = "\n I am a first paragraph. \n \n I am a second paragraph that needs a spoiler tag. \n I am a third paragraph that does not need a tag, before or after. \n\n"
	Processed_string = wpts.add_multiline_spoiler_tag_if_multiple_line_returns_in_a_row(Initial_String)
	assert Processed_string == "I am a first paragraph.\n\n>!I am a second paragraph that needs a spoiler tag. \n I am a third paragraph that does not need a tag, before or after."