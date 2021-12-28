import src.Warframe_patchnotes_thief_script as wpts

def test_Check_Title_Validity():
	title = "PSA: TestTitle"
	Forum = "Test"
	
	formatted, valid = wpts.Check_Title_Validity(title, Forum)
	assert formatted == "TestTitle"
	assert valid==True
	
	title = "Update1+Hotfix1.1"
	Forum = "https://forums.warframe.com/forum/3-pc-update-notes/"
	
	formatted, valid = wpts.Check_Title_Validity(title, Forum)
	assert valid==False
	
	
def test_split_content_for_character_limit():
	content = "TestParagraph1"
	result = wpts.split_content_for_character_limit(content, 15, ",")
	
	assert result == ("TestParagraph1","")

	
	content = "TestParagraph1,TestParagraph2,TestParagraph3"
	result = wpts.split_content_for_character_limit(content, 15, ",")
	
	assert result == ("TestParagraph1","TestParagraph2,TestParagraph3")
	
	
	content = "TestParagraph1.TestParagraph2,TestParagraph3"
	result = wpts.split_content_for_character_limit(content, 15, [",","."])
	
	assert result == ("TestParagraph1","TestParagraph2,TestParagraph3")
	
	content = "TestParagraph1"
	result = wpts.split_content_for_character_limit(content, 4)
	
	assert result == ("Test","Paragraph1")

def test_parse_forum_page_to_pull_latest_posts():
	with open("tests/source_for_test_parse_forum_page_to_pull_latest_posts.html") as file:
		contents = file.read()
	
	ResultHyperlink = wpts.parse_forum_page_to_pull_latest_posts(contents)
	assert ResultHyperlink["href"]=="https://forums.warframe.com/topic/1293591-the-new-war-hotfix-3105/"
	assert ResultHyperlink["title"].strip() == "The New War: Hotfix 31.0.5"

def Get_and_Parse_Notes():
	pass