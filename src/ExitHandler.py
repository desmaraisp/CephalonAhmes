import logging, sys, signal, atexit
from selenium import webdriver
from src import (
        S3BucketFunctions as s3b,
        LoggingUtilities,
        SubmissionsModels as models,
)

class SigintIgnore:
    sigint_detected: bool = False
    
    def __call__(self, _, __):
        self.sigint_detected = True

class ExitHandlerClass:
    _browser: webdriver.Chrome
    _post_history : models.SubmissionModelsForAllForumSources
    _sigint_ignore : SigintIgnore = SigintIgnore()

    def ExitFunction(self):
        s3b.push_post_history_to_bucket(self._post_history)
        LoggingUtilities.commit_string_logger_to_bucket()
        self._browser.quit()

    def excepthook(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.getLogger().critical("Uncaught exception",
                exc_info=(exc_type, exc_value, exc_traceback))

    def set_self_as_signal_handler(self):
        signal.signal(signal.SIGTERM, self)
        signal.signal(signal.SIGINT, self)


    def __init__(self, browser: webdriver.Chrome, post_history : models.SubmissionModelsForAllForumSources):
        self._post_history = post_history
        self._browser = browser

        self.set_self_as_signal_handler()
        sys.excepthook = self.excepthook
        atexit.register(self.ExitFunction)

    def __call__(self, _, __):
        sys.exit()
        

    def enable_lock(self):
        signal.signal(signal.SIGTERM, self._sigint_ignore)
        signal.signal(signal.SIGINT,  self._sigint_ignore)

    def disable_lock(self):
        self.set_self_as_signal_handler()
        if(self._sigint_ignore.sigint_detected):
            self.__call__(None, None)