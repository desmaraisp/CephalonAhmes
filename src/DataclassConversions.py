from src import SubmissionsModels as dtc
import dataclass_wizard


def convert_post_history_model_to_json(post_history: dtc.SubmissionModelsForAllForumSources) -> dict:
    return dataclass_wizard.asdict(post_history)


def convert_post_history_json_to_submission_model(json: dict) -> dtc.SubmissionModelsForAllForumSources:
    return dataclass_wizard.fromdict(dtc.SubmissionModelsForAllForumSources, json)
