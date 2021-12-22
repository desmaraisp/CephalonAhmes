import praw
import html2text as htt
from bs4 import BeautifulSoup
import re
import numpy as np
from webdriver_manager.chrome import ChromeDriverManager
import time, boto3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os, signal, sys, json, requests
import dpath.util as dpu




DEBUG_Source_Forum=True #False on release
DEBUG_subreddit = True #False on release
CloudCubeFilePath = os.environ["CLOUD_CUBE_BASE_LOC"]+"/PostHistory.json"
sleeptime=60



sort_menu_xpath='//a[@data-role="sortButton"]'
post_date_sort_xpath='//li[@data-ipsmenuvalue="start_date"]'
warframe_forum_urls={False:["https://forums.warframe.com/forum/3-pc-update-notes/","https://forums.warframe.com/forum/123-developer-workshop-update-notes/", "https://forums.warframe.com/forum/170-announcements-events/"],True:["https://forums.warframe.com/forum/36-general-discussion/"]}[DEBUG_Source_Forum]
target_SUB_Dict_Live={False:"scrappertest",True:"warframe"}
target_SUB_Dict_Debug={False:"scrappertest",True:"scrappertest"}
target_SUB_Dict = {True:target_SUB_Dict_Debug, False:target_SUB_Dict_Live}[DEBUG_subreddit]




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



def start_reddit_session():
	bot_login=praw.Reddit(
		client_id = os.environ["PRAW_CLIENT_ID"],
		client_secret = os.environ["PRAW_CLIENT_SECRET"],
		user_agent = 'warframe patch notes retriever bot 0.1',
		username = os.environ["PRAW_USERNAME"],
		password = os.environ["PRAW_PASSWORD"],validate_on_submit=True)
	bot_login.validate_on_submit=True
	return bot_login

def start_cloudcube_session():
	session_cloudcube = boto3.Session(
		aws_access_key_id=os.environ["CLOUDCUBE_ACCESS_KEY_ID"],
		aws_secret_access_key=os.environ["CLOUDCUBE_SECRET_ACCESS_KEY"],
	)
	s3 = session_cloudcube.resource('s3')
	return s3.Object('cloud-cube',CloudCubeFilePath)


def process_div_comment(soup):
	div_comment=soup.find('div',{"data-role":"commentContent"})
	
	for block in div_comment.find_all("blockquote"):
		block.find("div").decompose()
			
	for spoilerheader in div_comment.find_all("div",{"class":"ipsSpoiler_header"}):
		spoilerheader.decompose()
	
	if div_comment.find_all('span',{"class":'ipsType_reset ipsType_medium ipsType_light'}):
		div_comment.find('span',{"class":'ipsType_reset ipsType_medium ipsType_light'}).decompose() #removes edited tags
	
	for strong in div_comment.find_all("strong"):
		if strong.find_all('br')!=[]: #if there's any breakpoints in the strong tag, split the strong into smaller strongs
			brs_list=[s.extract() for s in strong.find_all('br')]
			strong_text_list=strong.get_text(strip=True,separator='\n').split('\n')
			strong.string=strong_text_list[0]
			for i in strong_text_list[1:]:
				newstrong=soup.new_tag("strong")
				newstrong.string=i
				for br in brs_list:strong.parent.strong.insert_after(br)
				strong.parent.insert(-1,newstrong)
		if strong.string:strong.string=strong.string.strip()
		elif strong.text:
			if strong.find('a'):
				for _ in strong.find_all("a"):
					_.unwrap()
			new_tag = soup.new_tag("strong")
			new_tag.string=strong.text.replace('\xa0','').strip()
			strong.insert_after(new_tag)
			strong.decompose()
				
	
	for i in div_comment.find_all("img"):
		if i.parent.name=="a":
			image_source=i.parent["href"]
			i.parent["href"]=None
			i["src"]=image_source
		elif i.parent.parent.name=="a":
			image_source=i.parent.parent["href"]
			i.parent.parent["href"]=None
			i["src"]=image_source
	
	for i in div_comment.find_all("source",{"type":"video/mp4"}):
		video_source=i["src"]
		i.parent.find('a')['href']=video_source
	
	
	for i in div_comment.find_all("iframe",{"class":'ipsEmbed_finishedLoading'}):
		i.string=i['src'].replace("?do=embed",'')
			
	for i in div_comment.find_all('div',{"class":'ipsEmbeddedVideo'}):
		i.find('iframe').string=i.find('iframe')['data-embed-src']

	for i in div_comment.find_all('iframe',{"allow":"accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"}):
		i.string=i["data-embed-src"]
	
	for i in div_comment.find_all('iframe',{"allowfullscreen frameborder":"0"}):
		i.string=i["src"]
	
	for em in div_comment.find_all("em"):
		for strong in em.find_all("strong"):
			strong.string=f"**{strong.string}**"
			strong.unwrap()
		if em.string:em.string=em.string.strip()
			
	for table in div_comment.find_all('table'):
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
			
	return div_comment

def Check_Title_Validity(title, ForumPage):
	title=title.replace("PSA: ","").strip()
	
	if "+" in title and ForumPage == "https://forums.warframe.com/forum/3-pc-update-notes/":
		return title, False
	return title, True

def has_been_posted_to_subreddit(title, SUB):
	subreddit_new_list=[sub_new_post.title for sub_new_post in start_reddit_session().subreddit(SUB).new(limit=10)]
	return title in subreddit_new_list

def get_subreddit_flair_id(SUB):
	flair_template=list(start_reddit_session().subreddit(SUB).flair.link_templates)
	return next((item.get('id') for item in flair_template if item["text"] == "News"), next((item.get('id') for item in flair_template if item["text"] == "Discussion"), None))

def split_content_for_character_limit(content, limit, separators = ['\n']):
	content_before_limit = content[:limit]
	for separator in separators:
		contentSeparatorIndexes=[m.start() for m in re.finditer(separator, content_before_limit)]
		if contentSeparatorIndexes.len!=1:
			break

	return content[contentSeparatorIndexes:], content[:contentSeparatorIndexes]


def make_submission(SUB, content, title, news_flair_id):
	#Splitting and posting
	bot_login=start_reddit_session()
	
	Content_Before_Limit, content = split_content_for_character_limit(content, 40000, ['\n\n', '\n'])
	
	bot_login.subreddit(SUB).submit(title,selftext=Content_Before_Limit.strip(),flair_id=news_flair_id,send_replies=False)
	for submission in bot_login.redditor(os.environ["PRAW_USERNAME"]).new(limit=1):
		bot_login.redditor("desmaraisp").message("Cephalon Ahmes has posted something",title+", link: "+submission.url)
		
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
	div_comment=process_div_comment(soup)
	
	htt_conf=htt.HTML2Text()
	htt_conf.use_automatic_links=True
	htt_conf.body_width=0
	post_contents=htt_conf.handle(div_comment.decode_contents())
	
	#strip superfluous parts/correct mistakes
	post_contents=post_contents.replace("![",'[')


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
				
				if PostHistory_json[ForumPost["ForumPage"]]:
					PostHistory_json[ForumPost["ForumPage"]].pop()
				
				PostHistoryPayload_To_Add = ForumPost.copy()
				PostHistoryPayload_To_Add.pop("ForumPage")
				PostHistory_json[ForumPost["ForumPage"]].insert(0, PostHistoryPayload_To_Add)

				cloud_cube_object.put(Bucket='cloud-cube',Body=json.dumps(PostHistory_json).encode('utf-8'),Key=CloudCubeFilePath)
		sleep_func(sleeptime)
	
	
#%%

# =============================================================================
# post_notes("""
# https://forums.warframe.com/topic/1253565-update-29100-corpus-proxima-the-new-railjack/
# """,'scrappertest')
# 
# =============================================================================
if __name__=="__main__":
	main_loop(target_SUB_Dict)

