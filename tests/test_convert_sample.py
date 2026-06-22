import sys
import os
from pathlib import Path

# Add parent directory to path to import src modules
current_dir = os.path.dirname(os.path.abspath(__file__))
target_dir = os.path.join(current_dir, "..")
sys.path.insert(0, os.path.abspath(target_dir))

from src import convert_sample


def get_sample_titles() -> list[str]:
    """Get all sample HTML files without the .html extension."""
    samples_dir = os.path.join(os.getcwd(), "samples")
    titles = []
    for filename in os.listdir(samples_dir):
        if filename.endswith(".html"):
            title = os.path.splitext(filename)[0]
            titles.append(title)
    return sorted(titles)


def test_conversion_produces_no_delta_for_all_samples() -> None:
    """
    Test that converting all HTML samples produces identical markdown output
    to the existing markdown files (no delta). This is a regression test to
    ensure the conversion process is stable.
    """
    for title in get_sample_titles():
        # Run the conversion
        converted_markdown = convert_sample.convert_contents(title)
        
        # Read the existing markdown file
        markdown_path = os.path.join(os.getcwd(), "samples", f"{title}.md")
        with open(markdown_path, "r") as md_file:
            existing_markdown = md_file.read()
        
        # Ensure they match
        assert converted_markdown == existing_markdown, (
            f"Conversion delta detected for sample '{title}'. "
            f"The converted output does not match the existing markdown file."
        )