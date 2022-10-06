from typing import List, Optional, Tuple, Any
import attr
import typed_settings as ts

def ThrowValidationException(message: str) -> None:
    raise ValueError(message)

def NotEmptyValue(instance: Any, attribute: attr.Attribute, value: Any) -> None:
    if(not value):  ThrowValidationException(f"{attribute.name} must not be empty")

def NotEmptyItemsInList(instance: Any, attribute: attr.Attribute, value: List[Any]) -> None:
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
class GeneralSettings:
    XML_Urls: List[str] = ts.option(
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
