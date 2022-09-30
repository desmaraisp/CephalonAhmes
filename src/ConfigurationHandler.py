from typing import List, Optional, Tuple
import typed_settings as ts

def ThrowValidationException(message: str):
    raise ValueError(message)

def NotEmptyValue(instance, attribute, value):
    if(not value):  ThrowValidationException(f"{attribute.name} must not be empty")

def NotEmptyItemsInList(instance, attribute, value: List):
    if not all(value):
        ThrowValidationException(f"All items in {attribute.name} must not be empty")


@ts.settings()
class PrawSettings:
    PRAW_CLIENT_ID: str = ts.secret(
        validator= NotEmptyValue,
        default=""
    )
    PRAW_CLIENT_SECRET: str = ts.secret(
        validator= NotEmptyValue,
        default=""
    )
    PRAW_USERNAME: str = ts.secret(
        validator= NotEmptyValue,
        default=""
    )
    PRAW_PASSWORD: str = ts.secret(
        validator= NotEmptyValue,
        default=""
    )
    NotificationDestinationUsername: str = ts.option(
        validator= NotEmptyValue,
        default=""
    )
    SubredditDestinationFallbacks: List[str] = ts.option(
        validator= [NotEmptyValue, NotEmptyItemsInList],
        default=[]
    )
    Notify: bool = ts.option(default=True)

    
    
@ts.settings()
class S3Settings:
    PostHistoryFullFileName: str = ts.option(
        validator= NotEmptyValue,
        default=""
    )
    S3_BucketName: str = ts.option(
        validator= NotEmptyValue,
        default=""
    )

@ts.settings()
class RSSFeedInformation:
    XMLUrl: str = ts.option(
        validator= NotEmptyValue, 
        default=""
    )
    RefreshUrl: str = ts.option(default= None)

@ts.settings()
class GeneralSettings:
    forum_urls_list: List[RSSFeedInformation] = ts.option(
        validator= [ NotEmptyValue, NotEmptyItemsInList],
        default=[]
    )
    footer_message: str = ts.option(
        default=""
    )


def init_settings(current_configuration_name: Optional[str]) -> Tuple[PrawSettings, S3Settings, GeneralSettings]:
    config_files = ["settings.base.toml"]
    if(current_configuration_name and current_configuration_name!= 'base'):
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
