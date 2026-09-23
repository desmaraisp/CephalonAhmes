import argparse
import os
import sys
from typing import Optional
current_dir = os.path.dirname(os.path.abspath(__file__))
target_dir = os.path.join(current_dir, "..")
sys.path.insert(0, os.path.abspath(target_dir))
from src import (
    ConfigurationHandler as cfg,
    PrawUtilities as pru,
    StringManipulations
)



def main(title: Optional[str]) -> None:
    if(not title):
        print("Error: --title argument is required.")
        return

    sample = get_sample_contents(title)
    praw_settings, _, general_settings = cfg.init_settings("local")
    praw_utilities : pru.PrawUtilities = pru.PrawUtilities(praw_settings)

    praw_utilities.make_submission_to_targeted_subreddit(
        sample,
        StringManipulations.apply_many_regex_transforms(title, general_settings.title_replace)
    )

    return


def get_sample_contents(title: str) -> str:
    with open(os.path.join(os.getcwd(), "samples", f"{title}.md"), "r") as sample_file:
        html_content = sample_file.read()
    return html_content


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", help="Title of the sample to submit", dest="title", default=None)
    args = parser.parse_args()

    main(args.title)
