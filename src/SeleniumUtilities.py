from selenium import webdriver
from src import ConfigurationHandler as configuration_handler
from webdriver_manager.chrome import ChromeDriverManager

def start_chrome_browser() -> webdriver.Chrome:
    chrome_options = webdriver.chrome.options.Options()

    if(configuration_handler.PROJECTCONFIGURATION.GOOGLE_CHROME_BIN):
        chrome_options.binary_location = configuration_handler.PROJECTCONFIGURATION.GOOGLE_CHROME_BIN
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')

    return webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
