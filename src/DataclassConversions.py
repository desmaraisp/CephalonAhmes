import typing
from src import Models as dtc
import dataclass_wizard

def convert_post_history_model_to_json(post_history: dtc.SubmissionListForMultipleSources) -> typing.Dict:
    return dataclass_wizard.asdict(post_history)


def convert_post_history_json_to_submission_model(json: typing.Dict) -> dtc.SubmissionListForMultipleSources:
    return dataclass_wizard.fromdict(dtc.SubmissionListForMultipleSources, json)
