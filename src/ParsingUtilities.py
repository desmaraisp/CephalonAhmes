from datetime import datetime
import html
from typing import List
import html2text as htt
from bs4 import BeautifulSoup
from lxml import etree
from src import(
    Models as dtc,
    HTMLCorrections
)



def GetLastItemInformation(value: str) -> dtc.SubmissionModel | None:
    soup: etree._Element = etree.fromstring(value)
    items: List[etree._Element] = soup.findall('.//item')
    lastItem: etree._Element = max(items, key=get_date_from_node)
    guid_text = lastItem.find('./guid')
    if guid_text is None or guid_text.text is None:
        return None

    title_text = lastItem.find('./title')
    if title_text is None or title_text.text is None:
        return None
    
    description_text = lastItem.find('./description')
    if description_text is None or description_text.text is None:
        return None

    link = lastItem.find('./link')
    if link is None or link.text is None:
        return None
    
    date = get_date_from_node(lastItem)
    if date is None:
        return None

    return dtc.SubmissionModel(
        guid=int(guid_text.text),
        pub_date=date,
        title=title_text.text,
        contents=description_text.text,
        link=link.text
    )

def get_date_from_node(node: etree._Element) -> datetime:
    pubdate = node.find('./pubDate')
    if pubdate is None or pubdate.text is None:
        return datetime.min
    try:
        return datetime.strptime(pubdate.text, '%a, %d %b %Y %H:%M:%S %z')
    except ValueError:
        return datetime.min

def transform_contents_to_markdown(contents: str, url: str, footer:str) -> str:
    soup = BeautifulSoup(contents, 'html.parser')
    HTMLCorrections.process_html_tag(soup)

    htt_conf = htt.HTML2Text()
    htt_conf.use_automatic_links = True
    htt_conf.body_width = 0

    post_contents = htt_conf.handle(soup.decode_contents())
    # Because Reddit's implementation of markdown does not support inline links like this: ![]()
    post_contents = post_contents.replace("![", '[')
    post_contents = html.unescape(post_contents)

    post_contents = "[Source]({})\n\n{}\n------\n{}".format(
            url, post_contents, footer)

    return post_contents