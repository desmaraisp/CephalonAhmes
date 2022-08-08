import requests, logging
from selenium import webdriver
import selenium.common.exceptions as sce
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src import SleepHandler

def get_response_text_from_generic_url(url: str):
    success = False
    while not success:
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
        except:
            logging.getLogger().warning("Request Failed, retrying...")
            SleepHandler.SLEEPHANDLER.sleep(5000)
            continue
        success = True
    return response.text

def browser_fetch_updated_forum_page_source(forum_url: str, browser: webdriver.Chrome) -> str:
    sort_menu_xpath = '//a[@data-role="sortButton"]'
    post_date_sort_xpath = '//li[@data-ipsmenuvalue="start_date"]'

    while True:
        try:
            browser.get(forum_url)
            WebDriverWait(browser, 20).until(
                    EC.element_to_be_clickable((By.XPATH, sort_menu_xpath))).click()
            WebDriverWait(browser, 20).until(EC.element_to_be_clickable(
                    (By.XPATH, post_date_sort_xpath))).click()
            WebDriverWait(browser, 20).until_not(
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="elAjaxLoading"]')))
        except:
            logging.getLogger().warning("Selenium Error encountered, retrying...")
            SleepHandler.SLEEPHANDLER.sleep(5000)
            continue
        try:
            browser.find_element_by_tag_name('time')
            return browser.page_source
        except sce.NoSuchElementException:
            SleepHandler.SLEEPHANDLER.sleep(5000)
            logging.getLogger().warning("No time element found in selenium page, retrying...")
            continue
