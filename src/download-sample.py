import argparse
import os
import sys
from typing import List, cast
from lxml import etree
current_dir = os.path.dirname(os.path.abspath(__file__))
target_dir = os.path.join(current_dir, "..")
sys.path.insert(0, os.path.abspath(target_dir))
from src import (
        WebRequestMethods
)
import logging

def main(rss_feed_url: str, title: str) -> None:
    response = WebRequestMethods.get_response_from_generic_url(rss_feed_url)
    
    if(response.headers.get('expires', '0') != '0'):
        logging.warning(f"Getting cached data from website. Expires at {response.headers['expires']}")
        
    rss_feed_content = response.text
    sample_search = cast(List[etree._Element], etree.XML(rss_feed_content).xpath(f"//item[title='{title}']"))
    
    sample_item = sample_search[0] if sample_search else None
    
    if sample_item is None:
        logging.error("No sample found using the provided title")
        return
    
    description = sample_item.find("description")
    if description is None or description.text is None:
        logging.error("No description found for the sample item")
        return
    
    os.makedirs(os.path.join(os.getcwd(), "samples"), exist_ok=True)
    with open(os.path.join(os.getcwd(), "samples", f"{title}.html"), "w") as sample_file:
        sample_file.write(description.text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rss-feed-url", help="URL of the RSS feed to download", dest="rss_feed_url")
    parser.add_argument("--title", help="Title of the sample to download", dest="title")
    args = parser.parse_args()

    main(args.rss_feed_url, args.title)
