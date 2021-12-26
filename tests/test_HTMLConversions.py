from src.Warframe_patchnotes_thief_script import add_multiline_spoiler_tag_if_multiple_line_returns_in_a_row

def test_add_multiline_spoiler_tag_if_multiple_line_returns_in_a_row():
	Initial_String = "\n I am a first paragraph. \n \n I am a second paragraph that needs a spoiler tag. \n I am a third paragraph that does not need a tag, before or after. \n\n"
	Processed_string = add_multiline_spoiler_tag_if_multiple_line_returns_in_a_row(Initial_String)
	assert Processed_string == "I am a first paragraph.\n\n>!I am a second paragraph that needs a spoiler tag. \n I am a third paragraph that does not need a tag, before or after."
	

def test_strip_BlockQuote_Header():
	#HTML_Corrections.strip_BlockQuote_Header(tag)
	return