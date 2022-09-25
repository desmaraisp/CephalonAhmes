from bs4 import (
        element as bs4elem,
        BeautifulSoup
        )
from typing import Union
import re

def decompose_all_blockquote_headers(tag: Union[bs4elem.Tag, bs4elem.NavigableString]) -> None:
    for block in tag.find_all("blockquote"):
        block.find("div").decompose()


def decompose_all_spoiler_headers(tag: Union[bs4elem.Tag, bs4elem.NavigableString]) -> None:
    for spoilerheader in tag.find_all("div",{"class":"ipsSpoiler_header"}):
        spoilerheader.decompose()


def decompose_all_edited_on_footers(tag: Union[bs4elem.Tag, bs4elem.NavigableString]):
    for footer in tag.find_all('span',{"class":'ipsType_reset ipsType_medium ipsType_light'}):
        footer.decompose()


def strip_image_links_to_avoid_double_links(tag: Union[bs4elem.Tag, bs4elem.NavigableString]):
    for image in tag.find_all("img"):
        for link in image.find_parents('a'):
            image_source=link["href"]
            link["href"]=None
            image["src"]=image_source


def convert_mp4_to_link(tag: Union[bs4elem.Tag, bs4elem.NavigableString]):
    for source_element in tag.find_all("source",{"type":"video/mp4"}):
        video_source=source_element["src"]
        source_element.parent.find('a')['href']=video_source



def strip_heading_or_trailing_tabs_and_spaces_but_keep_newlines(string) -> str:
    def my_replace(match):
        return match.group().replace("\t","").replace(" ","")

    pattern = r'^\s*(?=\S)|(?<=\S)\s*$' #all trailing or leading whitespaces

    newstring = re.sub(pattern, my_replace,string)

    return newstring


def eliminate_and_propagate_tag(root_tag: Union[bs4elem.Tag, bs4elem.NavigableString], tag_name :str, soup: BeautifulSoup):
    for tag_of_type in root_tag.find_all(tag_name):
        for navigable_string in tag_of_type.find_all(string=True, recursive=True):
            newtag = soup.new_tag(tag_name)
            navigable_string.wrap(newtag)
            newtag.string = strip_heading_or_trailing_tabs_and_spaces_but_keep_newlines(newtag.string) #Removes spaces in the text to reduce incidence of spaces making markdown formatting not work

        tag_of_type.name="span"


def propagate_elements_to_children(tag: Union[bs4elem.Tag, bs4elem.NavigableString], soup: BeautifulSoup):
    eliminate_and_propagate_tag(tag, 'em', soup)
    eliminate_and_propagate_tag(tag, 'strong', soup)


def convert_iframes_to_link(tag: Union[bs4elem.Tag, bs4elem.NavigableString], soup: BeautifulSoup):
    for iframe_element in tag.find_all("iframe"):
        newtag = soup.new_tag("a")

        if iframe_element.has_attr("data-embed-src"):
            newtag.string = iframe_element["data-embed-src"]
        elif iframe_element.has_attr("src"):
            newtag.string = iframe_element["src"]
        else:continue
        iframe_element.wrap(newtag)
        iframe_element.decompose()


def add_spoiler_tag_to_html_element(element, soup: BeautifulSoup):

    element_has_string_attribute = False
    for child in element.children:
        if not (str(type(child))=="<class 'bs4.element.NavigableString'>"):
            continue
        elif str(child).strip(' '):
            element_has_string_attribute = True

    if (element_has_string_attribute) and not element.findParent("li"):
        if element.name in ["p","span","div"]:
            element.insert(0, ">!")


def Process_Spoiler(soup: BeautifulSoup):
    for spoiler in soup.find_all("div",{"class":"ipsSpoiler"}):
        for br in spoiler.find_all("br"):
            br.decompose()

        add_spoiler_tag_to_html_element(spoiler, soup)


        for element in spoiler.find_all():
            add_spoiler_tag_to_html_element(element, soup)

        for element in spoiler.find_all("li"):
            newtag = soup.new_tag("span")
            newtag.string = ">!"
            element.wrap(newtag)

        for element in spoiler.findParents("li"):
            newtag = soup.new_tag("span")
            newtag.string = ">!"
            element.wrap(newtag)

def decompose_all_table_cell_children(table_cell : Union[bs4elem.Tag, bs4elem.NavigableString]):
    for obj in table_cell.find_all(recursive=True):
        obj.unwrap()

def replace_empty_table_cell_content_with_dash(table_cell : Union[bs4elem.Tag, bs4elem.NavigableString]):
    if not table_cell.text.strip():
        table_cell.string="-"

def process_tables(tag: Union[bs4elem.Tag, bs4elem.NavigableString]):
    for table in tag.find_all('table'):
        for table_cell in table.findChildren('td'):
            decompose_all_table_cell_children(table_cell)
            replace_empty_table_cell_content_with_dash(table_cell)





def process_html_tag(soup: BeautifulSoup, main_post_tag : Union[bs4elem.Tag, bs4elem.NavigableString] ):
    decompose_all_blockquote_headers(main_post_tag)
    decompose_all_spoiler_headers(main_post_tag)
    decompose_all_edited_on_footers(main_post_tag)
    strip_image_links_to_avoid_double_links(main_post_tag)
    convert_mp4_to_link(main_post_tag)
    convert_iframes_to_link(main_post_tag, soup)
    propagate_elements_to_children(main_post_tag, soup)
    process_tables(main_post_tag)
    Process_Spoiler(soup)