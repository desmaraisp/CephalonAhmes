import praw
import html2text as htt
from bs4 import BeautifulSoup
import re
import numpy as np
import time
import boto3
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import signal
import sys



chrome_options = webdriver.chrome.options.Options()
if os.environ.get("GOOGLE_CHROME_BIN")!=None:
	chromedriverpath=os.environ.get("CHROMEDRIVER_PATH")
	chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
else:
	chromedriverpath=r"C:\Users\Philippe\Documents\Python Scripts\Youtube Randomizer\chromedriver.exe"
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')
browser=webdriver.Chrome(executable_path=chromedriverpath,options=chrome_options)



#Bot conditions
bot_login=praw.Reddit(client_id = os.environ["praw_client_id"],
	             client_secret = os.environ["praw_client_secret"],
	             user_agent = 'warframe patch notes retriever bot 0.1',
	             username = os.environ["praw_username"],
	             password = os.environ["praw_password"],validate_on_submit=True)
bot_login.validate_on_submit=True

#cloudcube login
session_cloudcube = boto3.Session(
	aws_access_key_id=os.environ["aws_access_key_id"],
	aws_secret_access_key=os.environ["aws_secret_access_key"],
)
s3 = session_cloudcube.resource('s3')
cloud_cube_object=s3.Object('cloud-cube',os.environ["cloud_cube_file_loc"])


source_forum_is_updates=True #True on release
DEBUG_subreddit = False #False on release

sort_menu_xpath='//a[@data-role="sortButton"]'
post_date_sort_xpath='//li[@data-ipsmenuvalue="start_date"]'
warframe_forum_url_latest_update={True:"https://forums.warframe.com/forum/3-pc-update-notes/",False:"https://forums.warframe.com/forum/36-general-discussion/"}[source_forum_is_updates]
SUB={True:"scrappertest",False:"warframe"}[DEBUG_subreddit]


def post_notes(url:str):
	with requests.session() as session:
		response=session.get(url,timeout=20)
		soup=BeautifulSoup(response.text,'html.parser')
	div_comment=soup.find('div',{"data-role":"commentContent"})
	
	if div_comment.find_all("blockquote"):
		for block in div_comment.find_all("blockquote"):
			block.find("div").decompose()
			
	if div_comment.find_all("div",{"class":"ipsSpoiler_header"}):
		for spoilerheader in div_comment.find_all("div",{"class":"ipsSpoiler_header"}):
			spoilerheader.decompose()
	
	if div_comment.find_all('span',{"class":'ipsType_reset ipsType_medium ipsType_light'})!=[]:
		div_comment.find('span',{"class":'ipsType_reset ipsType_medium ipsType_light'}).decompose() #removes edited tags
	
	if div_comment.find_all("strong")!=[]:
		for strong in div_comment.find_all("strong"):
			strong.string=strong.string.strip(" ")
			if strong.find_all('br')!=[]:
				brs_list=[s.extract() for s in strong.find_all('br')]
				strong_text_list=strong.get_text(strip=True,separator='\n').split('\n')
				strong.string=strong_text_list[0]
				for i in np.arange(1,len(strong_text_list)):
					newstrong=soup.new_tag("strong")
					newstrong.string=strong_text_list[i]
					for br in brs_list:strong.parent.strong.insert_after(br)
					strong.parent.insert(-1,newstrong)
			if strong.string:strong.string=strong.string.strip(" ")
	
	if div_comment.find_all('img')!=[]:
		for i in div_comment.find_all("img"):
			if i.parent.name=="a":
				image_source=i.parent["href"]
				i.parent["href"]=None
				i["src"]=image_source
	
	if div_comment.find_all("source",{"type":"video/mp4"})!=[]:
		for i in div_comment.find_all("source",{"type":"video/mp4"}):
			video_source=i["src"]
			i.parent.find('a')['href']=video_source
	
	if div_comment.find_all('iframe',{"class":'ipsEmbed_finishedLoading'})!=[]:
		for i in div_comment.find_all("iframe",{"class":'ipsEmbed_finishedLoading'}):
			i.string=i['src'].strip("?do=embed")
	
	if div_comment.find_all('iframe',{"allow":"accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"})!=[]:
		for i in div_comment.find_all('iframe',{"allow":"accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"}):
			i.string=i["data-embed-src"]
	
	if div_comment.find_all('iframe',{"allowfullscreen frameborder":"0"})!=[]:
		for i in div_comment.find_all('iframe',{"allowfullscreen frameborder":"0"}):
			i.string=i["src"]
	
	if div_comment.find_all("em"):
		for em in div_comment.find_all("em"):
			em.string=em.string.strip(" ")
			if em.find_all("strong"):
				for strong in em:
					strong.unwrap()
					em.string=f"**{em.string}**"
	
	if div_comment.find('table')!=[]:
		for table in div_comment.find_all('table'):
			for ps in table.findChildren('p'):
				if ps.find_all(recursive=True):
					for obj in ps.find_all(recursive=True):
						obj.unwrap()
				ps.unwrap()



	htt_conf=htt.HTML2Text()
	htt_conf.use_automatic_links=True
	htt_conf.body_width=0
	final_post=htt_conf.handle(div_comment.decode_contents())
	
	#strip superfluous parts/correct mistakes
	final_post=final_post.replace("![",'[')


	#title and url
	title_pre_split=soup.title.decode_contents()
	title_split_index=[m.start() for m in re.finditer("-",title_pre_split)]
	title=htt_conf.handle(title_pre_split[:title_split_index[-2]-1]).replace("PSA: ","")
	if "+" in title and "PC Update Notes" in title_pre_split:
		return
	automatic_message="\n------\n^(This action was performed automatically, if you see any mistakes, please tag /u/desmaraisp, he'll fix them.) [^(Here is my github)](https://github.com/CephalonAhmes/CephalonAhmes)"
	final_post="[Source]("+url+")\n\n"+final_post+automatic_message
	soup.decompose()


	
	#Splitting and posting
	flair_template=list(bot_login.subreddit(SUB).flair.link_templates)
	news_flair_id=next((item.get('id') for item in flair_template if item["text"] == "News"), next((item.get('id') for item in flair_template if item["text"] == "Discussion"), None))
	if len(final_post)>40000:
		split_arg=np.array([m.start() for m in re.finditer('\n\n', final_post[:40000])])[-1]
		if split_arg==0:split_arg=np.array([m.start() for m in re.finditer('\n', final_post[:40000])])[-1]
		final_post1,final_post2=final_post[:split_arg],final_post[split_arg:]
		bot_login.subreddit(SUB).submit(title,selftext=final_post1,flair_id=news_flair_id,send_replies=False)
		for submission in bot_login.redditor(os.environ["praw_username"]).new(limit=1):
			bot_login.redditor("desmaraisp").message("Cephalon Ahmes has posted something",title+", link: "+submission.url)
		time.sleep(5)
		while True:
			if len(final_post2)>10000:
				split_arg=np.array([m.start() for m in re.finditer('\n\n', final_post2[:10000])])[-1]
				if split_arg==0:split_arg=np.array([m.start() for m in re.finditer('\n', final_post2[:10000])])[-1]
				final_post1,final_post2=final_post2[:split_arg],final_post2[split_arg:]
				for comment in bot_login.redditor(os.environ["praw_username"]).new(limit=1):
					comment.reply(final_post1).disable_inbox_replies()
					time.sleep(5)
			else:
				for submission in bot_login.redditor(os.environ["praw_username"]).new(limit=1):
					submission.reply(final_post2).disable_inbox_replies()
				break
		
	else:
		bot_login.subreddit(SUB).submit(title,selftext=final_post,flair_id=news_flair_id,send_replies=False)
		for submission in bot_login.redditor(os.environ["praw_username"]).new(limit=1):
			bot_login.redditor("desmaraisp").message("Cephalon Ahmes has posted something",title+", link: "+submission.url)

	
def fetch_url(forums_url_list):
	newest_urls_array=[]
	newest_titles_array=[]
	for forum_url in forums_url_list:
		success=False
		while not success:
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
			newest_urls_array.append(parent_of_time_element_of_thread_list[arg_of_most_recent_thread].parent.find('a')['href'])
			newest_titles_array.append(parent_of_time_element_of_thread_list[arg_of_most_recent_thread].parent.find('a')['title'])
	return(np.array(newest_urls_array,dtype='<U255'),np.array(newest_titles_array,dtype='<U255'))
	soup.decompose()

def graceful_exit(a,b):
	browser.quit()
	sys.exit()

def sleep_func(sleeptime):
	duration=2
	for i in np.arange(0,sleeptime,duration):
		time.sleep(duration)

post_notes("""
https://forums.warframe.com/topic/1225874-heart-of-deimos-update-2910/
""")
#%%
# fetch newest pc update note post from forum
sleeptime=60
signal.signal(signal.SIGTERM,graceful_exit)
while True:
	last_posted_urls_array=np.array(cloud_cube_object.get()['Body'].read().decode('utf-8').split('\n'),dtype='<U255')[:len(np.array(cloud_cube_object.get()['Body'].read().decode('utf-8').split('\n'),dtype='<U255'))//2]
	last_posted_titles_array=np.array(cloud_cube_object.get()['Body'].read().decode('utf-8').split('\n'),dtype='<U255')[len(np.array(cloud_cube_object.get()['Body'].read().decode('utf-8').split('\n'),dtype='<U255'))//2:]
	try:
		forums_url_list=[warframe_forum_url_latest_update,'https://forums.warframe.com/forum/123-developer-workshop-update-notes/','https://forums.warframe.com/forum/170-announcements-events/']
		newest_urls_array,newest_titles_array=fetch_url(forums_url_list)
	except TimeoutException:
		print("Timeout")
		sleep_func(sleeptime)
		continue
	for i in range(len(newest_urls_array)):
		if newest_urls_array[i] not in last_posted_urls_array:
			if newest_titles_array[i] not in last_posted_titles_array:
				print(newest_titles_array[i])
				post_notes(newest_urls_array[i])
				last_posted_urls_array[i+2*len(forums_url_list)]=last_posted_urls_array[i+len(forums_url_list)]
				last_posted_urls_array[i+len(forums_url_list)]=last_posted_urls_array[i]
				last_posted_urls_array[i]=newest_urls_array[i]
				last_posted_titles_array[i+(2*len(forums_url_list))]=last_posted_titles_array[i+len(forums_url_list)]
				last_posted_titles_array[i+len(forums_url_list)]=last_posted_titles_array[i]
				last_posted_titles_array[i]=newest_titles_array[i]
	cloud_cube_object.put(Bucket='cloud-cube',Body="\n".join(np.concatenate((last_posted_urls_array,last_posted_titles_array))).encode('utf-8'),Key=os.environ["cloud_cube_file_loc"])
	sleep_func(sleeptime)