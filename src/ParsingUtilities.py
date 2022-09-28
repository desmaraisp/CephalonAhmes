from datetime import datetime
import html
import html2text as htt
from bs4 import BeautifulSoup
from src import(
    SubmissionsModels as dtc,
    ParsingUtilities,
    StringManipulations,
    HTMLCorrections
)


def get_post_element_from_full_discussion(soup: BeautifulSoup):
    return soup.find('div', {"data-role": "commentContent"})

def get_date_from_thread(thread):
    time_element_of_thread = thread.findChild('time', recursive=True)['datetime']
    return datetime.strptime(time_element_of_thread, '%Y-%m-%dT%H:%M:%SZ')

def get_latest_submission_dataclass_in_forum_page(page_source :str) -> dtc.IndividualSubmissionModel:
    soup = BeautifulSoup(page_source, "html.parser")
    list_of_all_threads_in_forum_page = soup.find(
            'ol', {'data-role': 'tableRows'}).find_all('div', {'class': 'ipsDataItem_main'})

    list_of_all_threads_in_forum_page = [a for a in list_of_all_threads_in_forum_page if a.findChild('time', recursive=True)]
    last_thread = max(list_of_all_threads_in_forum_page, key=get_date_from_thread)

    link_to_latest_post = last_thread.findChild('a', recursive=True)

    return dtc.IndividualSubmissionModel(
            link_to_latest_post["title"].strip(),
            link_to_latest_post["href"].strip()
    )

def transform_response_contents_to_markdown(ResponseContent, url: str, footer:str):
    ResponseContent = StringManipulations.remove_all_zero_width_spaces(ResponseContent)

    soup = BeautifulSoup(ResponseContent, 'html.parser')
    main_post_tag = ParsingUtilities.get_post_element_from_full_discussion(soup)
    HTMLCorrections.process_html_tag(soup, main_post_tag)

    htt_conf = htt.HTML2Text()
    htt_conf.use_automatic_links = True
    htt_conf.body_width = 0

    post_contents = htt_conf.handle(main_post_tag.decode_contents())
    # Because Reddit's implementation of markdown does not support inline links like this: ![]()
    post_contents = post_contents.replace("![", '[')
    post_contents = html.unescape(post_contents)

    post_contents = "[Source]({})\n\n{}\n------\n{}".format(
            url, post_contents, footer)

    return post_contents