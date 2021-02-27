import signal
from selenium.common.exceptions import TimeoutException
import Warframe_patchnotes_thief_script as wpts
import numpy as np
import os

def integration_test():
	os.environ["CHROMEDRIVER_PATH"]= os.environ["CHROMEWEBDRIVER"]+"/chromedriver"
	browser=wpts.start_chrome_browser()
	signal.signal(signal.SIGTERM,wpts.signal_handler(browser))
	while True:
		try:
			forums_url_list=[wpts.warframe_forum_url_latest_update,'https://forums.warframe.com/forum/123-developer-workshop-update-notes/','https://forums.warframe.com/forum/170-announcements-events/']
			newest_urls_array,newest_titles_array=wpts.fetch_url(forums_url_list, browser)
			break
		except TimeoutException:
			print("Timeout")
			wpts.sleep_func(4)
			continue
	selected_url=np.random.choice(newest_urls_array)
	print(selected_url)
	wpts.post_notes(selected_url,'scrappertest')
	wpts.sleep_func(4)
	browser.quit()
		



