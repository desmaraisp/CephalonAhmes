from bs4 import (
        element as bs4elem,
        BeautifulSoup
        )
import re

def decompose_all_blockquote_headers(soup: BeautifulSoup) -> None:
    for block in soup.find_all("blockquote"):
        block.find("div").decompose()


def decompose_all_spoiler_headers(soup: BeautifulSoup) -> None:
    for spoilerheader in soup.find_all("div",{"class":"ipsSpoiler_header"}):
        spoilerheader.decompose()


def decompose_all_edited_on_footers(soup: BeautifulSoup):
    for footer in soup.find_all('span',{"class":'ipsType_reset ipsType_medium ipsType_light'}):
        footer.decompose()


def strip_image_links_to_avoid_double_links(soup: BeautifulSoup):
    for image in soup.find_all("img"):
        for link in image.find_parents('a'):
            image_source=link["href"]
            link["href"]=None
            image["src"]=image_source


def convert_mp4_to_link(soup: BeautifulSoup):
    for source_element in soup.find_all("source",{"type":"video/mp4"}):
        video_source=source_element["src"]
        source_element.parent.find('a')['href']=video_source



def strip_heading_or_trailing_tabs_and_spaces_but_keep_newlines(string) -> str:
    def my_replace(match: re.Match):
        return match.group().replace("\t","").replace(" ","")

    pattern = r'^\s*(?=\S)|(?<=\S)\s*$' #all trailing or leading whitespaces

    return re.sub(pattern, my_replace, string)


def eliminate_and_propagate_tag(soup: BeautifulSoup, tag_name :str):
    tag: bs4elem.Tag
    for tag in soup.find_all(tag_name):
        
        navigable_string: bs4elem.NavigableString
        for navigable_string in tag.find_all(string=True, recursive=True):
            newtag = soup.new_tag(tag_name)
            navigable_string.wrap(newtag)
            newtag.string = strip_heading_or_trailing_tabs_and_spaces_but_keep_newlines(newtag.string) #Removes spaces in the text to reduce incidence of spaces making markdown formatting not work

        tag.name="span"


def propagate_elements_to_children(soup: BeautifulSoup):
    eliminate_and_propagate_tag(soup, 'em')
    eliminate_and_propagate_tag(soup, 'strong')


def convert_iframes_to_link(soup: BeautifulSoup):
    tag: bs4elem.Tag
    for tag in soup.find_all("iframe"):
        newtag = soup.new_tag("a")

        if tag.has_attr("data-embed-src"):
            newtag.string = tag["data-embed-src"]
        elif tag.has_attr("src"):
            newtag.string = tag["src"]
        else:continue
        tag.wrap(newtag)
        tag.decompose()


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
    spoiler: bs4elem.Tag
    for spoiler in soup.find_all("div",{"class":"ipsSpoiler"}):
        
        element: bs4elem.Tag
        for element in spoiler.find_all("br"):
            element.decompose()

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

def decompose_all_table_cell_children(table_cell : bs4elem.Tag):
    obj: bs4elem.Tag
    for obj in table_cell.find_all(recursive=True):
        obj.unwrap()

def replace_empty_table_cell_content_with_dash(table_cell : bs4elem.Tag):
    if not table_cell.text.strip():
        table_cell.string="-"

def process_tables(soup: BeautifulSoup):
    tag: bs4elem.Tag
    for tag in soup.find_all('table'):
        for table_cell in tag.findChildren('td'):
            decompose_all_table_cell_children(table_cell)
            replace_empty_table_cell_content_with_dash(table_cell)





def process_html_tag(soup: BeautifulSoup):
    decompose_all_blockquote_headers(soup)
    decompose_all_spoiler_headers(soup)
    decompose_all_edited_on_footers(soup)
    strip_image_links_to_avoid_double_links(soup)
    convert_mp4_to_link(soup)
    convert_iframes_to_link(soup)
    propagate_elements_to_children(soup)
    process_tables(soup)
    Process_Spoiler(soup)