from dataclasses import dataclass, field
import typing
from dataclass_wizard import JSONWizard
from dataclass_wizard.enums import LetterCase

class GlobalMetaClass(JSONWizard.Meta):
    key_transform_with_dump = LetterCase.SNAKE
    key_transform_with_load = LetterCase.SNAKE


@dataclass
class IndividualSubmissionModel(JSONWizard):
    submission_title: str
    submission_url: str


@dataclass
class SubmissionModelsForSingleForumSource(JSONWizard):
    submission_source_forum_url: str
    submissions_list: typing.List[IndividualSubmissionModel]


@dataclass
class SubmissionModelsForAllForumSources(JSONWizard):
    forum_sources: typing.List[SubmissionModelsForSingleForumSource] = field(default_factory=list)

    def find_forum_source_model_by_url(self, url_to_search_for: str) -> SubmissionModelsForSingleForumSource:
        return next(
                (forum_source for forum_source in self.forum_sources if forum_source.submission_source_forum_url == url_to_search_for),
                None
        )

