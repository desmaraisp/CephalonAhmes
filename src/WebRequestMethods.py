import requests, time
from requests.adapters import HTTPAdapter, Retry
from selenium import webdriver
import selenium.common.exceptions as sce
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import func_timeout
from retry.api import retry_call

def get_response_from_generic_url(url: str, MaxRetries: int = 5) -> requests.Response:
    session = requests.Session()

    retries = Retry(total=MaxRetries,
                    backoff_factor=0.1,
                    status_forcelist=[ 500, 502, 503, 504 ],
                    raise_on_status=True,
                )

    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        return session.get(url, timeout=20)
    except Exception as e:
        raise Exception("HTTP failure for '{}'.".format(url)) from e

def check_page_success(browser: webdriver.Chrome):
    browser.find_element(By.TAG_NAME, 'time')
    
def navigate_to_force_data_reload(browser : webdriver.Chrome):
    sort_menu_xpath = '//a[@data-role="sortButton"]'
    post_date_sort_xpath = '//li[@data-ipsmenuvalue="start_date"]'
    
    WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, sort_menu_xpath))).click()
    WebDriverWait(browser, 10).until(EC.element_to_be_clickable(
            (By.XPATH, post_date_sort_xpath))).click()
    WebDriverWait(browser, 10).until_not(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="elAjaxLoading"]')))

def browser_fetch_updated_forum_page_source_safely(forum_url: str, browser: webdriver.Chrome, retries: int = 3):
    return retry_call(
                fetch_timeout_wrapper,
                fargs = [forum_url, browser],
                exceptions=(func_timeout.exceptions.FunctionTimedOut, sce.NoSuchElementException),
                tries=retries, delay=0.1
            )
    
def fetch_timeout_wrapper(forum_url: str, browser: webdriver.Chrome):
    return func_timeout.func_timeout(10, browser_fetch_updated_forum_page_source, (forum_url, browser))

    
def browser_fetch_updated_forum_page_source(forum_url: str, browser: webdriver.Chrome) -> str:
    browser.get(forum_url)
    time.sleep(1)
    print("PAGE SOURCE")
    print(browser.page_source)
    check_page_success(browser)
    
    navigate_to_force_data_reload(browser)

    check_page_success(browser)
    return browser.page_source
