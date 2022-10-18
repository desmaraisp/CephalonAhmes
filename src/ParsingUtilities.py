from datetime import datetime
import html
import html2text as htt
from bs4 import BeautifulSoup
from lxml import etree
from src import(
    Models as dtc,
    StringManipulations,
    HTMLCorrections
)



def GetLastItemInformation(value: str) -> dtc.SubmissionModel:
    soup: etree._ElementTree = etree.fromstring(value)
    items: etree._Element = soup.findall('.//item')
    lastItem: etree._Element = max(items, key=get_date_from_node)
    return dtc.SubmissionModel(
        guid=int(lastItem.find('./guid').text),
        pub_date=get_date_from_node(lastItem),
        title=lastItem.find('./title').text,
        contents=lastItem.find('./description').text,
        link = lastItem.find('./link').text
    )

def get_date_from_node(node: etree._Element) -> datetime:
    pubdate: str = node.find('./pubDate').text
    return datetime.strptime(pubdate, '%a, %d %b %Y %H:%M:%S %z')

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