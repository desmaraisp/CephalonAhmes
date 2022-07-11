import os
import typing


class Default():
    MaxIterations = 1
    Iteration_Interval_Time = 0
    PrimaryDestinationSubreddit = "scrappertest"
    SecondaryDestinationSubreddit = "scrappertest"
    PostHistoryFileName = "SubmissionHistory.Default.json"
    LoggingConfigFileName = "logging.ini"
    LogFileName = "Default.log"
    GOOGLE_CHROME_BIN = os.getenv('GOOGLE_CHROME_BIN', None)
    PRAW_CLIENT_ID = os.getenv('PRAW_CLIENT_ID')
    PRAW_CLIENT_SECRET = os.getenv('PRAW_CLIENT_SECRET')
    PRAW_USERNAME = os.getenv('PRAW_USERNAME')
    PRAW_PASSWORD = os.getenv('PRAW_PASSWORD')
    CLOUDCUBE_ACCESS_KEY_ID = os.getenv('CLOUDCUBE_ACCESS_KEY_ID')
    CLOUDCUBE_SECRET_ACCESS_KEY = os.getenv('CLOUDCUBE_SECRET_ACCESS_KEY')
    CLOUD_CUBE_BASE_LOC = os.getenv('CLOUD_CUBE_BASE_LOC')
    BotOwnerUsername = 'desmaraisp'
    forum_urls_list = [
            "https://forums.warframe.com/forum/36-general-discussion/"
        ]


class Live(Default):
    PrimaryDestinationSubreddit = "warframe"
    MaxIterations = -1
    Iteration_Interval_Time = 60000
    LogFileName = "Live.log"
    PostHistoryFileName = "SubmissionHistory.Live.json"
    forum_urls_list = [
            "https://forums.warframe.com/forum/3-pc-update-notes/",
            "https://forums.warframe.com/forum/123-developer-workshop-update-notes/",
            "https://forums.warframe.com/forum/170-announcements-events/"
    ]

class CatchUp(Live):
    PrimaryDestinationSubreddit = "scrappertest"
    MaxIterations = 1
    Iteration_Interval_Time = 0


ConfigurationClasses:typing.Dict[str, Default] = {
    "Default":Default,
    "Live":Live,
    "CatchUp":CatchUp
}