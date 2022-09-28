from selenium import webdriver
from tempfile import mkdtemp
from selenium.webdriver.chrome.service import Service


def start_chrome_browser() -> webdriver.Chrome:
    chrome_options: webdriver.ChromeOptions = webdriver.chrome.options.Options()

    chrome_options.binary_location = '/opt/chrome/chrome'
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-dev-tools")
    chrome_options.add_argument("--no-zygote")
    chrome_options.add_argument(f"--user-data-dir={mkdtemp()}")
    chrome_options.add_argument(f"--data-path={mkdtemp()}")
    chrome_options.add_argument(f"--disk-cache-dir={mkdtemp()}")

    return webdriver.Chrome(service=Service("/opt/chromedriver"),
                            options=chrome_options)
