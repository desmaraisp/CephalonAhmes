from typing import List, Tuple
import typed_settings as ts


@ts.settings()
class PrawSettings:
    NotificationDestinationUsername: str = ""
    SubredditDestinationFallbacks: List[str] = []
    Notify: bool = False
    PRAW_CLIENT_ID: str = ts.secret(default="")
    PRAW_CLIENT_SECRET: str = ts.secret(default="")
    PRAW_USERNAME: str = ts.secret(default="")
    PRAW_PASSWORD: str = ts.secret(default="")
    
    
@ts.settings()
class S3Settings:
    PostHistoryFullFileName: str = ""
    S3_BucketName: str = ""


@ts.settings()
class GeneralSettings:
    forum_urls_list: List[str] = []
    footer_message: str = ""


def init_settings(current_configuration_name: str) -> Tuple[PrawSettings, S3Settings, GeneralSettings]:
    config_files = ["settings.toml"]
    if(current_configuration_name):
        config_files.append(f"settings.{current_configuration_name}.toml")

    praw_settings: PrawSettings = ts.load(
        cls=PrawSettings, config_file_section="PrawSettings", appname="cephalonahmes", config_files=config_files
    )
    s3_settings: S3Settings = ts.load(
        cls=S3Settings, config_file_section="S3Settings", appname="cephalonahmes", config_files=config_files
    )
    parsing_settings: GeneralSettings = ts.load(
        cls=GeneralSettings, config_file_section="GeneralSettings", appname="cephalonahmes", config_files=config_files
    )
    
    return praw_settings, s3_settings, parsing_settings
