import praw
import html2text as htt
from bs4 import BeautifulSoup
import re
import numpy as np
import time
import boto3
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os

#%%

chrome_options = Options()
if os.environ.get("GOOGLE_CHROME_BIN")!=None:
 	chromedriverpath=os.environ.get("CHROMEDRIVER_PATH")
 	chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
else:
	chromedriverpath="chromedriver.exe"
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')

#%%
#Bot conditions
bot_login=praw.Reddit(client_id = os.environ["praw_client_id"],
	             client_secret = os.environ["praw_client_secret"],
	             user_agent = 'warframe patch notes retriever bot 0.1',
	             username = os.environ["praw_username"],
	             password = os.environ["praw_password"],validate_on_submit=True)
bot_login.validate_on_submite=True

#cloudcube login
session_cloudcube = boto3.Session(
	aws_access_key_id=os.environ["aws_access_key_id"],
    aws_secret_access_key=os.environ["aws_secret_access_key"],
)
s3 = session_cloudcube.resource('s3')
cloud_cube_object=s3.Object('cloud-cube',os.environ["cloud_cube_file_loc"])


prints=False #False on release
source_forum_is_updates=True #True on release
DEBUG_subreddit = False #False on release

sort_menu_xpath='//a[@data-role="sortButton"]'
post_date_sort_xpath='//li[@data-ipsmenuvalue="start_date"]'
if source_forum_is_updates:
	warframe_forum_url_latest_update="https://forums.warframe.com/forum/3-pc-update-notes/"
else:
	warframe_forum_url_latest_update="https://forums.warframe.com/forum/36-general-discussion/"


if DEBUG_subreddit:
    SUB = "scrappertest"
else:
    SUB = "warframe"
	
#%%	
def post_notes(url:str):
	with requests.session() as session:
		response=session.get(url,timeout=20)
		soup=BeautifulSoup(response.text,'html.parser')
	div_comment=soup.find('div',{"data-role":"commentContent"})
	if div_comment.find_all('span',{"class":'ipsType_reset ipsType_medium ipsType_light'})!=[]:
		div_comment.find('span',{"class":'ipsType_reset ipsType_medium ipsType_light'}).decompose() #removes edited tags
	if div_comment.find_all("strong")!=[]:
		for strong in div_comment.find_all("strong"):
			if strong.find_all('br')!=[]:
				brs_list=[s.extract() for s in strong.find_all('br')]
				strong_text_list=strong.get_text(strip=True,separator='\n').split('\n')
				strong.string=strong_text_list[0]
				for i in np.arange(1,len(strong_text_list)):
					newstrong=soup.new_tag("strong")
					newstrong.string=strong_text_list[i]
					for br in brs_list:strong.parent.strong.insert_after(br)
					strong.parent.insert(-1,newstrong)
	if div_comment.find_all('img')!=[]:
		for i in div_comment.find_all("img"):
			if i.parent.name=="a":
				image_source=i.parent["href"]
				i.parent["href"]=None
				i["src"]=image_source
	if div_comment.find_all('video')!=[]:
		for i in div_comment.find_all("video"):
			video_source=i.find("source")["src"]
			i.find('a')['href']=video_source

	htt_conf=htt.HTML2Text()
	htt_conf.use_automatic_links=True
	htt_conf.body_width=0
	
	#strip superfluous parts/correct mistakes
	final_post=(htt_conf.handle(div_comment.decode_contents()))
	final_post=final_post.replace("\n\n|\n\n",'|')
	final_post=final_post.replace("![",'[')
	final_post=final_post.replace("\n--",'--').replace("--  \n",'--')
	final_post=final_post.replace("<",'')
	final_post=final_post.replace(">",'') #Might break some things if we ever need < or >.
	final_post=final_post.replace("_**_**",'_**')
	final_post=final_post.replace("**_**_",'**_')
	
	#title and url
	title=soup.title.decode_contents().partition("-")[0]
	if "+" in title:
		split_title=title.split("+")
		hotfix_name=split_title[-1]
		hotfix_split_index=[m.start() for m in re.finditer(hotfix_name.strip(" "), final_post)][0]
		hotfix_split_index=[m.start() for m in re.finditer("\n", final_post[:hotfix_split_index])][-1]
		hotfix_notes=final_post[hotfix_split_index:]
		for submission in bot_login.redditor(os.environ["praw_username"]).new(limit=1):
			submission.reply(hotfix_notes).disable_inbox_replies()
		return
	automatic_message="\n------\n^(This action was performed automatically, if you see any mistakes, please tag /u/desmaraisp, he'll fix them.) [^(Here is my github)](https://github.com/CephalonAhmes/CephalonAhmes)"
	final_post="[Source]("+url+")\n\n"+final_post+automatic_message
	soup.decompose()


	
	#Splitting and posting	
	if len(final_post)>37000:
		double_skips=np.array([m.start() for m in re.finditer('\n\n', final_post)])
		split_arg=double_skips[np.argmin(np.abs(double_skips-37000))]
		final_post1,final_post2=final_post[:split_arg],final_post[split_arg:]
		flair_template=list(bot_login.subreddit(SUB).flair.link_templates)
		news_flair_id=next((item.get('id') for item in flair_template if item["text"] == "News"), False)
		bot_login.subreddit(SUB).submit(title,selftext=final_post1,flair_id=news_flair_id,send_replies=False)
		time.sleep(5)
		while True:
			if len(final_post2)>9500:
				double_skips=np.array([m.start() for m in re.finditer('\n', final_post2)])
				split_arg=double_skips[np.argmin(np.abs(double_skips-9500))]
				final_post1,final_post2=final_post2[:split_arg],final_post2[split_arg:]
				for comment in bot_login.redditor(os.environ["praw_username"]).new(limit=1):
					comment.reply(final_post1).disable_inbox_replies()
					time.sleep(5)
			else:
				for submission in bot_login.redditor(os.environ["praw_username"]).new(limit=1):
					submission.reply(final_post2).disable_inbox_replies()
				break
		
	else:
		flair_template=list(bot_login.subreddit(SUB).flair.link_templates)
		news_flair_id=next((item.get('id') for item in flair_template if item["text"] == "News"), False)
		bot_login.subreddit(SUB).submit(title,selftext=final_post,flair_id=news_flair_id,send_replies=False)
	
def fetch_url(forums_url_list):
	with webdriver.Chrome(executable_path=chromedriverpath,options=chrome_options) as browser:
		newest_urls_array=[]
		for forum_url in forums_url_list:
			browser.get(forum_url)
			WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH,sort_menu_xpath))).click()
			WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH,post_date_sort_xpath))).click()
			WebDriverWait(browser, 20).until_not(EC.visibility_of_element_located((By.XPATH,'//*[@id="elAjaxLoading"]')))
			soup=BeautifulSoup(browser.page_source,"html.parser")
			parent_of_time_element_of_thread=soup.find_all('div',{'class':'ipsDataItem_meta ipsType_reset ipsType_light ipsType_blendLinks'})
			list_of_all_dates=[]
			for i in parent_of_time_element_of_thread:
				time_element_of_thread=i.findChild('time',recursive=True)['datetime']
				date=time_element_of_thread.strip('Z')
				list_of_all_dates.append(date)
			arg_of_most_recent_thread=np.array(list_of_all_dates,dtype='datetime64').argmax()
			newest_urls_array.append(parent_of_time_element_of_thread[arg_of_most_recent_thread].parent.find('a')['href'])
		browser.quit()
	return(np.array(newest_urls_array,dtype='<U255'))
	soup.decompose()
	
#%%
# fetch newwest pc update note post from forum
sleeptime=60
while True:
	last_posted_urls_array=np.array(cloud_cube_object.get()['Body'].read().decode('utf-8').split('\n'),dtype='<U255')
	if prints==True:print("opening browser")
	try:
		forums_url_list=[warframe_forum_url_latest_update,'https://forums.warframe.com/forum/123-developer-workshop-update-notes/','https://forums.warframe.com/forum/2-pc-announcements/','https://forums.warframe.com/forum/170-announcements-events/']
		newest_urls_array=fetch_url(forums_url_list)
	except TimeoutException:
		print("Timeout")
		time.sleep(sleeptime)
		continue
	if (newest_urls_array!=last_posted_urls_array).any():
		if prints==True:print("posting")
		posting_url_index_in_list=np.where(newest_urls_array!=last_posted_urls_array)[0][0]
		post_notes(newest_urls_array[posting_url_index_in_list])
		last_posted_urls_array[posting_url_index_in_list]=newest_urls_array[posting_url_index_in_list]
		cloud_cube_object.put(Bucket='cloud-cube',Body="\n".join(last_posted_urls_array).encode('utf-8'),Key=os.environ["cloud_cube_file_loc"])
	if prints==True:print("sleeping")
	time.sleep(sleeptime)