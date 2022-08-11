from selenium import webdriver
from selenium.webdriver.chrome.service import Service
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
    
    chrome_service = Service(ChromeDriverManager().install())
    
    return webdriver.Chrome(service= chrome_service,options=chrome_options)
