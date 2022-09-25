import logging, sys, atexit
from selenium import webdriver
from src import (
        LoggingUtilities,
        S3Utilities
)

class ExitHandlerClass:
    _browser: webdriver.Chrome
    _s3_utilities: S3Utilities.S3Utilities

    def ExitFunction(self):
        logging.getLogger().info("Calling atexit function")
        self._browser.quit()

    def excepthook(self, exc_type, exc_value, exc_traceback):
        if not issubclass(exc_type, KeyboardInterrupt):
            logging.getLogger().critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    def __init__(self, browser: webdriver.Chrome, s3_utilities: S3Utilities.S3Utilities):
        self._browser = browser
        self._s3_utilities = s3_utilities

        sys.excepthook = self.excepthook
        atexit.register(self.ExitFunction)

    def __call__(self, _, __):
        logging.getLogger().warning("Signal handler called, exiting")
        sys.exit()