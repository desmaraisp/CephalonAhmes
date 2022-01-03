import praw
import html2text as htt
from bs4 import BeautifulSoup
import numpy as np
from webdriver_manager.chrome import ChromeDriverManager
import boto3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import dpath.util as dpu
import src.AhmesConfig as ahc

import os, signal, sys, json, requests, re, time, html, argparse, atexit, logging, logging.config, io

def start_chrome_browser():
	chrome_options = webdriver.chrome.options.Options()
	if ahc.env_config["GOOGLE_CHROME_BIN"]!='null':
		chrome_options.binary_location = ahc.env_config["GOOGLE_CHROME_BIN"]
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument("--disable-extensions")
	chrome_options.add_argument("--disable-gpu")
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('--disable-dev-shm-usage')
	return webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)

def start_reddit_session():
	bot_login=praw.Reddit(
		client_id = ahc.env_config["PRAW_CLIENT_ID"],
		client_secret = ahc.env_config["PRAW_CLIENT_SECRET"],
		user_agent = 'warframe patch notes retriever bot 0.1',
		username = ahc.env_config["PRAW_USERNAME"],
		password = ahc.env_config["PRAW_PASSWORD"],
		validate_on_submit=True,
		check_for_async=False
		)
	bot_login.validate_on_submit=True
	return bot_login

def get_cloudcube_object(filename):
	session_cloudcube = boto3.Session(
		aws_access_key_id=ahc.env_config["CLOUDCUBE_ACCESS_KEY_ID"],
		aws_secret_access_key=ahc.env_config["CLOUDCUBE_SECRET_ACCESS_KEY"],
	)
	s3 = session_cloudcube.resource('s3')
	return s3.Object('cloud-cube',ahc.env_config["CLOUD_CUBE_BASE_LOC"]+filename)



class HTML_Corrections:
	@staticmethod
	def strip_BlockQuote_Header(tag):
		for block in tag.find_all("blockquote"):
			block.find("div").decompose()

	@staticmethod
	def strip_Spoiler_Header(tag):
		for spoilerheader in tag.find_all("div",{"class":"ipsSpoiler_header"}):
			spoilerheader.decompose()

	@staticmethod
	def strip_Edited_Footer(tag):
		for footer in tag.find_all('span',{"class":'ipsType_reset ipsType_medium ipsType_light'}):
			footer.decompose()

	@staticmethod
	def strip_image_links_to_avoid_double_links(tag):
		for image in tag.find_all("img"):
			for link in image.find_parents('a'):
				image_source=link["href"]
				link["href"]=None
				image["src"]=image_source
	
	@staticmethod
	def convert_mp4_to_link(tag):
		for source_element in tag.find_all("source",{"type":"video/mp4"}):
			video_source=source_element["src"]
			source_element.parent.find('a')['href']=video_source
				
	
	@staticmethod
	def strip_tabs_and_spaces_but_keep_newlines(string):
		def my_replace(match):
			return match.group().replace("\t","").replace(" ","")
		
		pattern = r'^\s*(?=\S)|(?<=\S)\s*$' #all trailing or leading whitespaces
		
		newstring = re.sub(pattern, my_replace,string)
		
		return newstring
		
	@staticmethod
	def recursive_function(element, tag_name, soup):
		for child in element.children:
			is_leaf_of_tree = (str(type(child))=="<class 'bs4.element.NavigableString'>")
			
			if not is_leaf_of_tree:
				HTML_Corrections.recursive_function(child, tag_name, soup)
			elif child.string.strip():
				newtag = soup.new_tag(tag_name)
				child.wrap(newtag)
				newtag.string = HTML_Corrections.strip_tabs_and_spaces_but_keep_newlines(newtag.string) #Removes spaces in the text to reduce incidence of spaces making markdown formatting not work
		if element.name == tag_name:
			element.name="span"
	
	@staticmethod
	def eliminate_and_propagate_tag(tag_object, tag_name, soup):
		for element in tag_object.find_all(tag_name):
			HTML_Corrections.recursive_function(element, tag_name, soup)
	
	@staticmethod
	def propagate_elements_to_children(tag, soup):
		HTML_Corrections.eliminate_and_propagate_tag(tag, 'em', soup)
		HTML_Corrections.eliminate_and_propagate_tag(tag, 'strong', soup)
			
	@staticmethod
	def convert_iframes_to_link(tag, soup):
		for iframe_element in tag.find_all("iframe"):
			newtag = soup.new_tag("a")
			
			if iframe_element.has_attr("data-embed-src"):
				newtag.string = iframe_element["data-embed-src"]
			elif iframe_element.has_attr("src"):
				newtag.string = iframe_element["src"]
			else:continue
			iframe_element.wrap(newtag)
			iframe_element.decompose()
	
	@staticmethod
	def add_spoiler_tag_to_html_element(element, soup):
		
		element_has_string_attribute = False
		for child in element.children:
			if not (str(type(child))=="<class 'bs4.element.NavigableString'>"):
				continue
			elif str(child).strip(' '):
				element_has_string_attribute = True
		
		if (element_has_string_attribute) and not element.findParent("li"):
			if element.name in ["p","span","div"]:
				element.insert(0, ">!")
	
	@staticmethod
	def Process_Spoiler(soup):
		for spoiler in soup.find_all("div",{"class":"ipsSpoiler"}):
			for br in spoiler.find_all("br"):
				br.decompose()
			
			HTML_Corrections.add_spoiler_tag_to_html_element(spoiler, soup)
			
			
			for element in spoiler.find_all():
				HTML_Corrections.add_spoiler_tag_to_html_element(element, soup)
				
			for element in spoiler.find_all("li"):
				newtag = soup.new_tag("span")
				newtag.string = ">!"
				element.wrap(newtag)
				
			for element in spoiler.findParents("li"):
				newtag = soup.new_tag("span")
				newtag.string = ">!"
				element.wrap(newtag)

	@staticmethod
	def Process_Tables(tag):
		for table in tag.find_all('table'):
			for tds in table.findChildren('td'):
				for obj in tds.find_all(recursive=True):
					obj.unwrap()
				if not tds.text.strip():
					tds.string="-"

def process_soup_to_pull_post_contents(soup):
	div_comment=soup.find('div',{"data-role":"commentContent"})
	
	HTML_Corrections.strip_BlockQuote_Header(div_comment)
	HTML_Corrections.strip_Spoiler_Header(div_comment)
	HTML_Corrections.strip_Edited_Footer(div_comment)
	HTML_Corrections.strip_image_links_to_avoid_double_links(div_comment)
	HTML_Corrections.convert_mp4_to_link(div_comment)
	HTML_Corrections.convert_iframes_to_link(div_comment, soup)
	HTML_Corrections.propagate_elements_to_children(div_comment, soup)
	HTML_Corrections.Process_Tables(div_comment)
	HTML_Corrections.Process_Spoiler(soup)
			
	return div_comment

def Check_Title_Validity(title, ForumPage):
	title=title.replace("PSA: ","").strip()
	
	if "+" in title and ForumPage == "https://forums.warframe.com/forum/3-pc-update-notes/":
		return title, False #Excludes hotfixes as they are mostly duplicates
	return title, True

def has_been_posted_to_subreddit(title, SUB):
	subreddit_new_list=[sub_new_post.title for sub_new_post in start_reddit_session().subreddit(SUB).new(limit=10)]
	return title in subreddit_new_list

def get_subreddit_flair_id(SUB):
	flair_template=list(start_reddit_session().subreddit(SUB).flair.link_templates)
	return next((item.get('id') for item in flair_template if item["text"] == "News"), next((item.get('id') for item in flair_template if item["text"] == "Discussion"), None))

def split_content_for_character_limit(content, limit, separators = ['\n']):
	if len(content)<=limit:
		return content, ''
	
	CurrentSeparatorLen = -1
	content_before_limit = content[:limit]
	for separator in separators:
		contentSeparatorIndexes=[m.start() for m in re.finditer(separator, content_before_limit)]
		if contentSeparatorIndexes:
			CurrentSeparatorLen = len(separator)
			break
	
	if CurrentSeparatorLen!=-1:
		return content[:contentSeparatorIndexes[-1]], content[contentSeparatorIndexes[-1]+CurrentSeparatorLen:]
	else:
		return content[:limit], content[limit:]


def make_submission(SubredditDict, content, title):
	#Splitting and posting
	bot_login=start_reddit_session()
	DestinationSubreddit = SubredditDict[not (has_been_posted_to_subreddit(title, SubredditDict[True]))]
	news_flair_id= get_subreddit_flair_id(DestinationSubreddit)
	
	Content_Before_Limit, content = split_content_for_character_limit(content, 40000, ['\n\n', '\n'])
	
	bot_login.subreddit(DestinationSubreddit).submit(title,selftext=Content_Before_Limit.strip(),flair_id=news_flair_id,send_replies=False)		
		
	for submission in bot_login.redditor(ahc.env_config["PRAW_USERNAME"]).new(limit=1):
		bot_login.redditor(ahc.env_config["BotOwnerUsername"]).message(title, submission.url)
		
	while content:
		Content_Before_Limit, content = split_content_for_character_limit(content, 10000, ['\n\n', '\n'])
		for comment in bot_login.redditor(ahc.env_config["PRAW_USERNAME"]).new(limit=1):
			comment.reply(Content_Before_Limit.strip()).disable_inbox_replies()
		

def GetNotes_From_Request(url:str):
	success = False
	while not success:
		try:
			response=requests.get(url,timeout=20)
			response.raise_for_status()
		except:
			logging.getLogger().warning("Request Failed, retrying...")
			time.sleep(5)
			continue
		success = True
	return response.text

def Get_and_Parse_Notes(ResponseContent, url:str, SubmissionTitle:str, ForumSourceURL):
	ResponseContent = ResponseContent.replace(u"\xa0", "") #Zero-width spaces are evil
	
	soup=BeautifulSoup(ResponseContent,'html.parser')
	post_contents_HTML=process_soup_to_pull_post_contents(soup)

	htt_conf=htt.HTML2Text()
	htt_conf.use_automatic_links=True
	htt_conf.body_width=0

	post_contents=htt_conf.handle(post_contents_HTML.decode_contents())
	post_contents=post_contents.replace("![",'[')  #Because Reddit's implmentation of markdown does not support inline links like this: ![]()
	post_contents=html.unescape(post_contents)


	SubmissionTitle, SubmissionValidTitle=Check_Title_Validity(SubmissionTitle, ForumSourceURL)
	if not SubmissionValidTitle:
		logging.getLogger().warning("Submission Ignored with title {}.".format(SubmissionTitle))
		return
	
	automatic_message="\n------\n^(This action was performed automatically, if you see any mistakes, please tag /u/{}, he'll fix them.) [^(Here is my github)](https://github.com/CephalonAhmes/CephalonAhmes)".format(ahc.env_config["BotOwnerUsername"])
	post_contents="[Source]({})\n\n{}{}".format(url,post_contents,automatic_message)

	return post_contents, SubmissionTitle

def browser_get_updated_forum_page_source(forum_url, browser):
	success=False
	sort_menu_xpath='//a[@data-role="sortButton"]'
	post_date_sort_xpath='//li[@data-ipsmenuvalue="start_date"]'
	
	while not success:
		try:
			browser.get(forum_url)
			WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH,sort_menu_xpath))).click()
			WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH,post_date_sort_xpath))).click()
			WebDriverWait(browser, 20).until_not(EC.visibility_of_element_located((By.XPATH,'//*[@id="elAjaxLoading"]')))
		except:
			logging.getLogger().warning("Selenium Error encountered, retrying...")
			time.sleep(5)
			continue
		if browser.find_element_by_tag_name('time'):
			return browser.page_source
		else:
			time.sleep(5)
			logging.getLogger().warning("No time element found in selenium page, retrying...")
			continue

def parse_forum_page_to_pull_latest_posts(page_source):
	soup=BeautifulSoup(page_source,"html.parser")
	Thread_element_root=soup.find('ol',{'data-role':'tableRows'}).find_all('div',{'class':'ipsDataItem_main'})
	
	list_of_all_dates=[]
	for i in Thread_element_root:
		time_element_of_thread=i.findChild('time',recursive=True)['datetime']
		date=time_element_of_thread.strip('Z')
		list_of_all_dates.append(date)

	arg_of_most_recent_thread=np.array(list_of_all_dates,dtype='datetime64').argmax()
	return Thread_element_root[arg_of_most_recent_thread].findChild('a',recursive=True)


def fetch_and_parse_forum_page_to_pull_latest_posts(forums_url_list, browser):
	newest_posts_on_warframe_forum=[]
	for forum_url in forums_url_list:
		page_source = browser_get_updated_forum_page_source(forum_url, browser)
		hyperlink_to_newest_post = parse_forum_page_to_pull_latest_posts(page_source)
		
		newest_posts_on_warframe_forum.append({
			"URL":hyperlink_to_newest_post["href"].strip(),
			"PageName":hyperlink_to_newest_post["title"].strip(),
			"ForumPage":forum_url
		})
	return newest_posts_on_warframe_forum


def cull_logs(string, maxlen):
	lines = string.split("\n")
	if len(lines)>maxlen:
		number_of_lines_to_cut = len(lines)-maxlen
		lines = lines[number_of_lines_to_cut:]
		string = "\n".join(lines)
	return string

class ExitHandlerClass:
	def ExitFunction(self):
		log_string = logging.getLogger().handlers[1].stream.getvalue()
		log_string = fetch_cloudcube_contents(ahc.env_config["LogFileName"]) + log_string
		log_string = cull_logs(log_string, 100)
		
		get_cloudcube_object(ahc.env_config["LogFileName"]).put(Body=log_string.encode('utf-8'))
		get_cloudcube_object(ahc.env_config["PostHistoryFileName"]).put(Body=json.dumps(self.PostHistory_json).encode('utf-8'))
		self.browser.quit()
		
	def excepthook(self, exc_type, exc_value, exc_traceback):
		if issubclass(exc_type, KeyboardInterrupt):
			sys.__excepthook__(exc_type, exc_value, exc_traceback)
			return
		logging.getLogger().critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

	def __init__(self, browser, PostHistory_json):
		self.PostHistory_json = PostHistory_json
		self.browser=browser
		signal.signal(signal.SIGTERM,self)
		sys.excepthook = self.excepthook
		atexit.register(self.ExitFunction)
		
		logging.config.fileConfig(ahc.env_config["LoggingConfigFileName"])

	def __call__(self,a,b):
		sys.exit()
	


def sleep_func(sleeptime):
	duration=2
	for i in np.arange(0,sleeptime,duration):
		time.sleep(duration)

def fetch_cloudcube_contents(filename):
	return get_cloudcube_object(filename).get()['Body'].read().decode('utf-8')

def commit_post_to_PostHistory(PostHistory_json, ForumPost):
	if len(PostHistory_json[ForumPost["ForumPage"]])>=3:
		PostHistory_json[ForumPost["ForumPage"]].pop()
	
	PostHistoryPayload_To_Add = ForumPost.copy()
	PostHistoryPayload_To_Add.pop("ForumPage")
	PostHistory_json[ForumPost["ForumPage"]].insert(0, PostHistoryPayload_To_Add)


def main_loop(MaxIterations, Iteration_Interval_Time, Get_Posts_From_General_Discussions_Page, Post_To_scrappertest_subreddit):
	"""
	Parameters
	----------
	Get_Posts_From_General_Discussions_Page : bool
		Whether the posted notes will be pulled from the intended forum pages (news, updates, etc) or from the general discussions page. Set to False for the news pages and True for General Discussions.
	Post_To_scrappertest_subreddit : bool
		Whether the posted notes will be posted in the scrappertest subreddit by default. Set to False to post to r/warframe or True scrappertest.
	"""
	
	target_SUB_Dict_Live={False:"scrappertest",True:"warframe"} #True for primary subreddit, False for backup option if the post was already made by DE
	target_SUB_Dict_Debug={False:"scrappertest",True:"scrappertest"}
	
	SubredditDict = {True:target_SUB_Dict_Debug, False:target_SUB_Dict_Live}[Post_To_scrappertest_subreddit]
	warframe_forum_urls={False:["https://forums.warframe.com/forum/3-pc-update-notes/","https://forums.warframe.com/forum/123-developer-workshop-update-notes/", "https://forums.warframe.com/forum/170-announcements-events/"],True:["https://forums.warframe.com/forum/36-general-discussion/"]}[Get_Posts_From_General_Discussions_Page]
	
	browser=start_chrome_browser()
	
	PostHistory_json=json.loads(fetch_cloudcube_contents(ahc.env_config["PostHistoryFileName"]))
	Exit_Handler = ExitHandlerClass(browser, PostHistory_json)
	CurrentIteration = 0
	
	while CurrentIteration != MaxIterations:
		newest_posts_on_warframe_forum=fetch_and_parse_forum_page_to_pull_latest_posts(warframe_forum_urls, browser)
		for i, ForumPost in enumerate(newest_posts_on_warframe_forum):
			
			condition1 = ForumPost["URL"] not in dpu.values(PostHistory_json, '/*/*/URL')
			condition2 = ForumPost["PageName"] not in dpu.values(PostHistory_json, '/*/*/PageName')
			if condition1 and condition2:
				ResponseContent = GetNotes_From_Request(ForumPost["URL"])
				SubmissionContents, SubmussionTitle = Get_and_Parse_Notes(ResponseContent, ForumPost["URL"], ForumPost["PageName"], ForumPost["ForumPage"])
				
				make_submission(SubredditDict, SubmissionContents, SubmussionTitle)
				logging.getLogger().warning(ForumPost["PageName"])
				commit_post_to_PostHistory(PostHistory_json, ForumPost)

		sleep_func(Iteration_Interval_Time)
		CurrentIteration += 1
	
	
#%%


if __name__=="__main__":
	main_loop(ahc.env_config["MaxIterations"], ahc.env_config["Iteration_Interval_Time"], ahc.env_config["Get_Posts_From_General_Discussions_Page"], ahc.env_config["Post_To_scrappertest_subreddit"])
