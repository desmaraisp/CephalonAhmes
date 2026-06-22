from bs4 import (
        element as bs4elem,
        BeautifulSoup,
        )
import re

def decompose_all_blockquote_headers(soup: BeautifulSoup) -> None:
    block: bs4elem.Tag
    for block in soup.find_all("blockquote"):
        div = block.find("div")
        if(div is not None):
            div.decompose()

def decompose_all_span(soup: BeautifulSoup) -> None:
    # The span tags are used for formatting purposes, but they can cause issues with markdown formatting.
    # For example, if a span tag is used to make text bold, it can prevent the markdown syntax for bold from working properly.
    # By decomposing all span tags, we can get rid of a whole class of issues
    span: bs4elem.Tag
    for span in soup.find_all("span"):
        span.unwrap()


def decompose_all_b(soup: BeautifulSoup) -> None:
    # The <b> tags cause excessive bolding when converted to markdown, so we can just replace them with their text content
    b: bs4elem.Tag
    for b in soup.find_all("b"):
        b.unwrap()


def decompose_all_spoiler_headers(soup: BeautifulSoup) -> None:
    spoilerheader: bs4elem.Tag
    for spoilerheader in soup.find_all("div",{"class":"ipsSpoiler_header"}):
        spoilerheader.decompose()


def decompose_all_edited_on_footers(soup: BeautifulSoup) -> None:
    footer: bs4elem.Tag
    for footer in soup.find_all('span',{"class":'ipsType_reset ipsType_medium ipsType_light'}):
        footer.decompose()


def strip_image_links_to_avoid_double_links(soup: BeautifulSoup) -> None:
    image: bs4elem.Tag
    link: bs4elem.Tag
    for image in soup.find_all("img"):
        for link in image.find_parents('a'):
            image_source=link["href"]
            del link["href"]
            image["src"]=image_source


def convert_mp4_to_link(soup: BeautifulSoup) -> None:
    source_element: bs4elem.Tag
    for source_element in soup.find_all("source",{"type":"video/mp4"}):
        video_source=source_element["src"]
        
        parent = source_element.parent
        if(parent is None):
            continue
        
        anchor = parent.find('a')
        if anchor is None:
            continue
        
        anchor['href']=video_source



def decompose_all_strong(soup: BeautifulSoup) -> None:
    strong: bs4elem.Tag
    for strong in soup.find_all("strong"):
        text = strong.text

        if(not text.strip()):
            strong.unwrap()
            continue

        leading_ws = re.match(r'^\s*', text)
        prefix = f"{leading_ws.group() if leading_ws else ''}**"

        trailing_ws = re.search(r'\s*$', text)
        suffix = f"**{trailing_ws.group() if trailing_ws else ''}"

        strong.insert_after(f"{prefix}{text.strip()}{suffix}")
        strong.decompose()


def decompose_all_em(soup: BeautifulSoup) -> None:
    em: bs4elem.Tag
    for em in soup.find_all("em"):
        text = em.text
        if(not text.strip()):
            em.unwrap()
            continue

        leading_ws = re.match(r'^\s*', text)
        prefix = f"{leading_ws.group() if leading_ws else ''}_"

        trailing_ws = re.search(r'\s*$', text)
        suffix = f"_{trailing_ws.group() if trailing_ws else ''}"

        em.insert_after(f"{prefix}{text.strip()}{suffix}")
        em.decompose()


def convert_iframes_to_link(soup: BeautifulSoup) -> None:
    tag: bs4elem.Tag
    for tag in soup.find_all("iframe"):
        newtag = soup.new_tag("a")

        if tag.has_attr("data-embed-src"):
            newtag.string = str(tag["data-embed-src"])
        elif tag.has_attr("src"):
            newtag.string = str(tag["src"])
        else:continue
        tag.wrap(newtag)
        tag.decompose()


def process_spoiler(soup: BeautifulSoup) -> None:
    def internal(spoiler: bs4elem.Tag, tag_name: str) -> None:
        tag: bs4elem.Tag
        for tag in spoiler.find_all(tag_name):
            text = tag.text

            leading_ws = re.match(r'^\s*', text)
            prefix = f"{leading_ws.group() if leading_ws else ''}>!"

            trailing_ws = re.search(r'\s*$', text)
            suffix = f"!<{trailing_ws.group() if trailing_ws else ''}"

            tag.insert_after(soup.new_tag("p", string=f"{prefix}{text.strip()}{suffix}"))
            tag.decompose()

    spoiler: bs4elem.Tag
    for spoiler in soup.find_all("div",{"class":"ipsSpoiler"}):
        internal(spoiler, "p")
        internal(spoiler, "li")
        for list in spoiler.find_all(["ul", "ol"]):
            list.unwrap()


def decompose_all_table_cell_children(table_cell : bs4elem.Tag) -> None:
    obj: bs4elem.Tag
    for obj in table_cell.find_all(recursive=True):
        obj.unwrap()

def replace_empty_table_cell_content_with_dash(table_cell : bs4elem.Tag) -> None:
    if not table_cell.text.strip():
        table_cell.string = "-"

def process_tables(soup: BeautifulSoup) -> None:
    tag: bs4elem.Tag
    for tag in soup.find_all('table'):
        for table_cell in tag.find_all(['td','th']):
            decompose_all_table_cell_children(table_cell)
            replace_empty_table_cell_content_with_dash(table_cell)


def process_nested_lists(soup: BeautifulSoup, max_depth: int = 3) -> None:
    # Recurses through the entire doc to find deeply nested lists and "fake" them. This is necessary because Reddit does not support
    # lists nested more than three levels deep and the source HTML can have those.
    list_tag_names = ["ul","ol"]

    def recurse(tag: bs4elem.Tag, current_depth: int) -> None:
        for child in tag.find_all(recursive=False):
            if(child.name not in list_tag_names):
                recurse(child, current_depth)
                continue

            next_depth = current_depth + 1
            recurse(child, next_depth)

            if next_depth > max_depth:
                for li in child.find_all("li", recursive=False):
                    caret_container = soup.new_tag("span", string=f"⠀⠀‣")
                    li.insert_before(soup.new_tag("br"))
                    li.insert_before(caret_container)
                    li.unwrap()

                child.unwrap()

    recurse(soup, 0)

def process_html_tag(soup: BeautifulSoup) -> None:
    decompose_all_span(soup)
    decompose_all_em(soup)
    decompose_all_b(soup)
    decompose_all_strong(soup)
    decompose_all_blockquote_headers(soup)
    decompose_all_spoiler_headers(soup)
    decompose_all_edited_on_footers(soup)
    strip_image_links_to_avoid_double_links(soup)
    convert_mp4_to_link(soup)
    convert_iframes_to_link(soup)
    process_tables(soup)
    process_nested_lists(soup, 3)
    process_spoiler(soup)