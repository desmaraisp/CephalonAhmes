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
from selenium.common.exceptions import TimeoutException
import dpath.util as dpu
import os, signal, sys, json, requests, re, time




DEBUG_Source_Forum=True #False on release
DEBUG_subreddit = True #False on release
LOOP_mode=False #True on release
CloudCubeFilePath = os.environ["CLOUD_CUBE_BASE_LOC"]+"/PostHistory.json"
sleeptime=60



sort_menu_xpath='//a[@data-role="sortButton"]'
post_date_sort_xpath='//li[@data-ipsmenuvalue="start_date"]'
warframe_forum_urls={False:["https://forums.warframe.com/forum/3-pc-update-notes/","https://forums.warframe.com/forum/123-developer-workshop-update-notes/", "https://forums.warframe.com/forum/170-announcements-events/"],True:["https://forums.warframe.com/forum/36-general-discussion/"]}[DEBUG_Source_Forum]
target_SUB_Dict_Live={False:"scrappertest",True:"warframe"}
target_SUB_Dict_Debug={False:"scrappertest",True:"scrappertest"}
target_SUB_Dict = {True:target_SUB_Dict_Debug, False:target_SUB_Dict_Live}[DEBUG_subreddit]

htt_conf=htt.HTML2Text()
htt_conf.use_automatic_links=True
htt_conf.body_width=0


def start_chrome_browser():
	chrome_options = webdriver.chrome.options.Options()
	if os.environ.get("GOOGLE_CHROME_BIN"):
		chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument("--disable-extensions")
	chrome_options.add_argument("--disable-gpu")
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('--disable-dev-shm-usage')
	return webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)

def add_multiline_spoiler_tag_if_multiple_line_returns_in_a_row(string): #TODO check for necessity
	def add_character(match):
		return match.group+"\n\n>!"
	
	pattern = '\s+\n' #also includes if one line return, one space and one more line return
	return re.sub(pattern, add_character, string)

def start_reddit_session():
	bot_login=praw.Reddit(
		client_id = os.environ["PRAW_CLIENT_ID"],
		client_secret = os.environ["PRAW_CLIENT_SECRET"],
		user_agent = 'warframe patch notes retriever bot 0.1',
		username = os.environ["PRAW_USERNAME"],
		password = os.environ["PRAW_PASSWORD"],
		validate_on_submit=True,
		check_for_async=False
		)
	bot_login.validate_on_submit=True
	return bot_login

def start_cloudcube_session():
	session_cloudcube = boto3.Session(
		aws_access_key_id=os.environ["CLOUDCUBE_ACCESS_KEY_ID"],
		aws_secret_access_key=os.environ["CLOUDCUBE_SECRET_ACCESS_KEY"],
	)
	s3 = session_cloudcube.resource('s3')
	return s3.Object('cloud-cube',CloudCubeFilePath)

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
	def recursive_function(element, tag_name, soup):
		for child in element.children:
			is_leaf_of_tree = (type(child)!="<class 'bs4.element.NavigableString'>")
			
			newtag= soup.new_tag(tag_name)
			child.wrap(newtag)
			
			if not is_leaf_of_tree:
				HTML_Corrections.recursive_function(child, newtag)
		element.name="div"

	
	@staticmethod
	def eliminate_and_propagate_tag(tag_object, tag_name, soup):
		for element in tag_object.find_all(tag_name, recursive=True):
			HTML_Corrections.recursive_function(element, tag_name, soup)
	
	@staticmethod
	def propagate_elements_to_children(tag, soup):
		HTML_Corrections.eliminate_and_propagate_tag(tag, 'strong', soup)
		HTML_Corrections.eliminate_and_propagate_tag(tag, 'em', soup)
			
	@staticmethod
	def convert_iframes_to_link(tag, soup):
		for iframe_element in tag.find_all("iframe"):
			newtag = soup.new_tag("a")
			newtag.string = iframe_element["src"]
			iframe_element.wrap(newtag)
			iframe_element.decompose()
			
	@staticmethod
	def Process_Spoiler(tag):
		for spoiler in tag.find_all("div",{"class":"ipsSpoiler"}):
			spoiler_contents=htt_conf.handle(spoiler.decode_contents()).strip()
			spoiler_contents = ">!"+spoiler_contents
			spoiler_contents = add_multiline_spoiler_tag_if_multiple_line_returns_in_a_row(spoiler_contents)
			
			newtag = tag.new_tag("div")
			newtag.text = spoiler_contents
			spoiler.wrap(newtag)
			spoiler.decompose()

	@staticmethod
	def Process_Tables(tag):
		for table in tag.find_all('table'):
			for ps in table.findChildren('p'):
				for obj in ps.find_all(recursive=True):
					obj.unwrap()
				ps.unwrap()
			for tr in table.findChildren('tr'):
				td=tr.find('td')
				if not td.text:
					td.string="-"
				elif not td.text.strip():
					td.string="-"

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
	HTML_Corrections.Process_Spoiler(div_comment)
			
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
	content_before_limit = content[:limit]
	for separator in separators:
		contentSeparatorIndexes=[m.start() for m in re.finditer(separator, content_before_limit)]
		if contentSeparatorIndexes:
			break

	return content[:contentSeparatorIndexes[-1]], content[contentSeparatorIndexes[-1]:]


def make_submission(SUB, content, title, news_flair_id):
	#Splitting and posting
	bot_login=start_reddit_session()
	
	Content_Before_Limit, content = split_content_for_character_limit(content, 40000, ['\n\n', '\n'])
	
	bot_login.subreddit(SUB).submit(title,selftext=Content_Before_Limit.strip(),flair_id=news_flair_id,send_replies=False)		
		
	for submission in bot_login.redditor(os.environ["PRAW_USERNAME"]).new(limit=1):
		bot_login.redditor("desmaraisp").message(title, submission.url)
		
	while content:
		Content_Before_Limit, content = split_content_for_character_limit(content, 10000, ['\n\n', '\n'])
		for comment in bot_login.redditor(os.environ["PRAW_USERNAME"]).new(limit=1):
			comment.reply(Content_Before_Limit.strip()).disable_inbox_replies()
		

def post_notes(url:str, SubmissionTitle:str, ForumSourceURL,SubredditDict:str):
	success = False
	while not success:
		try:
			response=requests.get(url,timeout=20)
			response.raise_for_status()
		except:
			continue
		success = True
		
	soup=BeautifulSoup(response.text,'html.parser')
	post_contents_HTML=process_soup_to_pull_post_contents(soup)

	post_contents=htt_conf.handle(post_contents_HTML.decode_contents())
	post_contents=post_contents.replace("![",'[')  #Because Reddit's implmentation of markdown does not support inline links like this: ![]()


	SubmissionTitle, SubmissionValidTitle=Check_Title_Validity(SubmissionTitle, ForumSourceURL)
	if not SubmissionValidTitle:
		print(f"Submission Ignored with title {SubmissionTitle}.")
		return

	DestinationSubreddit = SubredditDict[not (has_been_posted_to_subreddit(SubmissionTitle, SubredditDict[True]))]

	
	automatic_message="\n------\n^(This action was performed automatically, if you see any mistakes, please tag /u/desmaraisp, he'll fix them.) [^(Here is my github)](https://github.com/CephalonAhmes/CephalonAhmes)"
	post_contents="[Source]("+url+")\n\n"+post_contents+automatic_message

	news_flair_id= get_subreddit_flair_id(DestinationSubreddit)
	make_submission(DestinationSubreddit, post_contents, SubmissionTitle, news_flair_id)

	
def fetch_url(forums_url_list, browser):
	newest_posts_on_warframe_forum=[]
	for forum_url in forums_url_list:
		success=False
		while not success: #TODO update this with requests if possible
			browser.get(forum_url)
			WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH,sort_menu_xpath))).click()
			WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH,post_date_sort_xpath))).click()
			WebDriverWait(browser, 20).until_not(EC.visibility_of_element_located((By.XPATH,'//*[@id="elAjaxLoading"]')))
			soup=BeautifulSoup(browser.page_source,"html.parser")
			parent_of_time_element_of_thread_list=soup.find_all('div',{'class':'ipsDataItem_meta ipsType_reset ipsType_light ipsType_blendLinks'})
			list_of_all_dates=[]
			for i in parent_of_time_element_of_thread_list:
				time_element_of_thread=i.findChild('time',recursive=True)['datetime']
				date=time_element_of_thread.strip('Z')
				list_of_all_dates.append(date)
			try:
				arg_of_most_recent_thread=np.array(list_of_all_dates,dtype='datetime64').argmax()
			except ValueError:
				print("404")
				time.sleep(20)
				continue
			success=True
			
			hyperlink_to_newest_post = parent_of_time_element_of_thread_list[arg_of_most_recent_thread].parent.find('a')
			
			newest_posts_on_warframe_forum.append({
				"URL":hyperlink_to_newest_post["href"].strip(),
				"PageName":hyperlink_to_newest_post["title"].strip(),
				"ForumPage":forum_url
			})
	return newest_posts_on_warframe_forum


class signal_handler:
	def __init__(self, browser):
		self.browser=browser
	def __call__(self,a,b):
		self.browser.quit()
		sys.exit()


def sleep_func(sleeptime):
	duration=2
	for i in np.arange(0,sleeptime,duration):
		time.sleep(duration)

def fetch_cloudcube_contents(cloud_cube_object):
	return json.loads(cloud_cube_object.get()['Body'].read().decode('utf-8'))

#%%
def main_loop(SUB):
	cloud_cube_object=start_cloudcube_session()
	browser=start_chrome_browser()
	signal.signal(signal.SIGTERM,signal_handler(browser))
	PostHistory_json=fetch_cloudcube_contents(cloud_cube_object)
	while True:
		try:
			newest_posts_on_warframe_forum=fetch_url(warframe_forum_urls, browser)
		except TimeoutException:
			print("Timeout")
			sleep_func(sleeptime)
			continue
		for i, ForumPost in enumerate(newest_posts_on_warframe_forum):
			condition1 = ForumPost["URL"] not in dpu.values(PostHistory_json, '/*/*/URL')
			condition2 = ForumPost["PageName"] not in dpu.values(PostHistory_json, '/*/*/PageName')
			if condition1 and condition2:
				print(ForumPost["PageName"])
				post_notes(ForumPost["URL"], ForumPost["PageName"], ForumPost["ForumPage"],SUB)
				
				if len(PostHistory_json[ForumPost["ForumPage"]])>=3:
					PostHistory_json[ForumPost["ForumPage"]].pop()
				
				PostHistoryPayload_To_Add = ForumPost.copy()
				PostHistoryPayload_To_Add.pop("ForumPage")
				PostHistory_json[ForumPost["ForumPage"]].insert(0, PostHistoryPayload_To_Add)

				cloud_cube_object.put(Bucket='cloud-cube',Body=json.dumps(PostHistory_json).encode('utf-8'),Key=CloudCubeFilePath)
		sleep_func(sleeptime)
	
	
#%%


if __name__=="__main__":
	if LOOP_mode:
		main_loop(target_SUB_Dict)
	else:
		post_notes(
			"https://forums.warframe.com/topic/1253565-update-29100-corpus-proxima-the-new-railjack/",
			'TestSubmssion',
			'',
			target_SUB_Dict
			)


