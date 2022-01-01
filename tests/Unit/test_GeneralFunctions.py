import src.Warframe_patchnotes_thief_script as wpts
import json, sys

def test_cull_logs():
	initial_string = "test1 \n test2 \n test3 \n test4"
	
	Expected = " test2 \n test3 \n test4"
	
	Result = wpts.cull_logs(initial_string, 3)
	
	assert Result == Expected
	

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
	with open("tests/Unit/source_for_test_parse_forum_page_to_pull_latest_posts.html") as file:
		contents = file.read()
	
	ResultHyperlink = wpts.parse_forum_page_to_pull_latest_posts(contents)
	assert ResultHyperlink["href"]=="https://forums.warframe.com/topic/1293591-the-new-war-hotfix-3105/"
	assert ResultHyperlink["title"].strip() == "The New War: Hotfix 31.0.5"
	
def test_commit_post_to_PostHistory():
	PostHistory_JSON = json.loads("""
	{
	    "https://forums.warframe.com/forum/170-announcements-events/": [
	        {
	            "PageName": "Test1",
	            "URL": "www.google.com"
	        }
	    ]
	}
	""")
	
	Expected = json.loads("""
	{
	    "https://forums.warframe.com/forum/170-announcements-events/": [
	        {
	            "PageName": "Test2",
	            "URL": "https://www.test.com"
	        },
	        {
	            "PageName": "Test1",
	            "URL": "www.google.com"
	        }
	    ]
	}
	""")

	
	
	ForumPost = {"URL":"https://www.test.com", "PageName":"Test2", "ForumPage":"https://forums.warframe.com/forum/170-announcements-events/"}
	
	wpts.commit_post_to_PostHistory(PostHistory_JSON, ForumPost)
	
	assert PostHistory_JSON == Expected
	
	
def test_commit_post_to_PostHistory2():
	PostHistory_JSON = json.loads("""
	{
	    "https://forums.warframe.com/forum/170-announcements-events/": [
	        {
	            "PageName": "Test1",
	            "URL": "www.google.com"
	        },
	        {
	            "PageName": "Test2",
	            "URL": "www.google.com"
	        },
	        {
	            "PageName": "Test3",
	            "URL": "www.google.com"
	        }
	    ]
	}
	""")
	
	Expected = json.loads("""
	{
	    "https://forums.warframe.com/forum/170-announcements-events/": [
	        {
	            "PageName": "Test4",
	            "URL": "https://www.test.com"
	        },
	        {
	            "PageName": "Test1",
	            "URL": "www.google.com"
	        },
	        {
	            "PageName": "Test2",
	            "URL": "www.google.com"
	        }
	    ]
	}
	""")

	
	
	ForumPost = {"URL":"https://www.test.com", "PageName":"Test4", "ForumPage":"https://forums.warframe.com/forum/170-announcements-events/"}
	
	wpts.commit_post_to_PostHistory(PostHistory_JSON, ForumPost)
	
	assert PostHistory_JSON == Expected
	
	
def test_Parse_CLI_Arguments():
	sys.argv[1:] = ["--ConfigurationName=Default"]
	
	Result = wpts.Parse_CLI_Arguments()
	
	assert Result == "Default"

def test_Parse_CLI_Arguments2():
	sys.argv[1:] = []
	
	Result = wpts.Parse_CLI_Arguments()
	
	assert Result == "Default"
