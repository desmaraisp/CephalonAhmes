from dataclasses import dataclass, field
import typing
from dataclass_wizard import JSONWizard
from dataclass_wizard.enums import LetterCase
from datetime import datetime

class GlobalMetaClass(JSONWizard.Meta):
    key_transform_with_dump = LetterCase.SNAKE
    key_transform_with_load = LetterCase.SNAKE


@dataclass
class SubmissionModel(JSONWizard):
    title: str = ""
    contents: str = ""
    pub_date: datetime = datetime.min
    guid: int = 0
    link: str = ""


@dataclass
class SubmissionsListForSingleSource(JSONWizard):
    rss_source_url: str
    submissions_list: typing.List[SubmissionModel] = field(default_factory=list)


@dataclass
class SubmissionListForMultipleSources(JSONWizard):
    forum_sources: typing.List[SubmissionsListForSingleSource] = field(default_factory=list)


    def add_submission(self, submission_model_to_add : SubmissionModel, rss_url: str) -> None:
        current_forum_source_in_history = next((i for i in self.forum_sources if i.rss_source_url == rss_url), None)

        if(not current_forum_source_in_history):
            self.forum_sources.append(SubmissionsListForSingleSource(
                rss_source_url= rss_url,
                submissions_list= [ submission_model_to_add ]
            ))
            return

        if len(current_forum_source_in_history.submissions_list) >= 3:
            current_forum_source_in_history.submissions_list.pop(0)

        current_forum_source_in_history.submissions_list.append(submission_model_to_add)
