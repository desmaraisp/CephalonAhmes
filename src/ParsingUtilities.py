from datetime import datetime
from bs4 import BeautifulSoup
from src import SubmissionsModels as dtc


def get_post_element_from_full_discussion(soup: BeautifulSoup):
    return soup.find('div', {"data-role": "commentContent"})

def get_date_from_thread(thread):
    time_element_of_thread = thread.findChild(
            'time', recursive=True)['datetime']

    return datetime.strptime(time_element_of_thread, '%Y-%m-%dT%H:%M:%SZ')

def get_latest_submission_dataclass_in_forum_page(page_source :str) -> dtc.IndividualSubmissionModel:
    soup = BeautifulSoup(page_source, "html.parser")
    list_of_all_threads_in_forum_page = soup.find(
            'ol', {'data-role': 'tableRows'}).find_all('div', {'class': 'ipsDataItem_main'})

    last_thread = max(list_of_all_threads_in_forum_page, key=lambda elem: get_date_from_thread(elem))

    link_to_latest_post = last_thread.findChild(
            'a', recursive=True)

    return dtc.IndividualSubmissionModel(
            link_to_latest_post["title"].strip(),
            link_to_latest_post["href"].strip()
    )
