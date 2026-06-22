import argparse
import os
import sys
from typing import Generator, Optional
current_dir = os.path.dirname(os.path.abspath(__file__))
target_dir = os.path.join(current_dir, "..")
sys.path.insert(0, os.path.abspath(target_dir))
from src import (
        ParsingUtilities
)


def main(title: Optional[str]) -> None:
    if(title):
        process_file(title)
        return
    
    for title in list_samples():
        process_file(title)


def list_samples() -> Generator[str]:
    for filename in os.listdir(os.path.join(os.getcwd(), "samples")):
        if filename.endswith(".html"):
            title = os.path.splitext(filename)[0]
            yield title

def process_file(title: str) -> None:
    submission_contents_markdown = convert_contents(title)
    
    os.makedirs(os.path.join(os.getcwd(), "samples"), exist_ok=True)
    with open(os.path.join(os.getcwd(), "samples", f"{title}.md"), "w") as sample_file:
        sample_file.write(submission_contents_markdown)

def convert_contents(title: str) -> str:
    html_content = get_sample_contents(title)
    
    return ParsingUtilities.transform_contents_to_markdown(
        html_content,
        "https://sample-src.com",
        "This is a sample footer"
    )

def get_sample_contents(title: str) -> str:
    with open(os.path.join(os.getcwd(), "samples", f"{title}.html"), "r") as sample_file:
        html_content = sample_file.read()
    return html_content


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", help="Title of the sample to convert", dest="title", default=None)
    args = parser.parse_args()

    main(args.title)
