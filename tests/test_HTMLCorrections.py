import src.HTMLCorrections as htmlc
from bs4 import BeautifulSoup
import html


def test_decompose_all_blockquote_headers_should_destroy_header_content() -> None:
    initial_string = """<blockquote><div>HeaderContent</div><div>StringContent</div></blockquote>"""

    DesiredResult = """<blockquote><div>StringContent</div></blockquote>"""

    tag = BeautifulSoup(initial_string, 'html.parser')

    htmlc.decompose_all_blockquote_headers(tag)

    assert tag.decode_contents()== DesiredResult

def test_decompose_strong_should_add_asterisks() -> None:
    initial_string = "<strong>test1</strong>"

    desired_result = "**test1**"

    soup = BeautifulSoup(initial_string, 'html.parser')
    htmlc.decompose_all_strong(soup)

    assert soup.decode_contents() == desired_result


def test_decompose_strong_should_keep_spaces() -> None:
    initial_string = " <strong> test1 </strong> "

    desired_result = "  **test1**  "

    soup = BeautifulSoup(initial_string, 'html.parser')
    htmlc.decompose_all_strong(soup)

    assert soup.decode_contents() == desired_result


def test_strip_spoiler_header_should_destroy_header() -> None:
    initial_string = """<div class="ipsSpoiler"><div class="ipsSpoiler_header">HeaderContents</div><div class="ipsSpoiler_contents">SpoilerContents</div></div>"""
    tag = BeautifulSoup(initial_string, 'html.parser')

    htmlc.decompose_all_spoiler_headers(tag)

    assert tag.decode_contents()=="""<div class="ipsSpoiler"><div class="ipsSpoiler_contents">SpoilerContents</div></div>"""

def test_strip_edited_footer_should_destroy_footer() -> None:
    initial_string = """<span class="ipsType_reset ipsType_medium ipsType_light"><strong>Edited by TestUser</strong></span>"""
    tag = BeautifulSoup(initial_string, 'html.parser')

    htmlc.decompose_all_edited_on_footers(tag)

    assert tag.decode_contents()==""

def test_strip_image_links_to_avoid_double_links() -> None:
    initial_string = """<a href="hreflink"><img src="imgsource"></a>"""
    tag = BeautifulSoup(initial_string, 'html.parser')

    htmlc.strip_image_links_to_avoid_double_links(tag)

    assert tag.decode_contents()=="""<a><img src="hreflink"/></a>"""

def test_strip_image_links_to_avoid_double_links2() -> None:
    initial_string = """<a href="hreflink"><div><img src="imgsource"></div></a>"""
    tag = BeautifulSoup(initial_string, 'html.parser')

    htmlc.strip_image_links_to_avoid_double_links(tag)

    assert tag.decode_contents()=="""<a><div><img src="hreflink"/></div></a>"""

def test_convert_mp4_to_link() -> None:
    initial_string = """<div><a href="SomeRandomHref"/><source type="video/mp4" src="srclink"/></div>"""
    tag = BeautifulSoup(initial_string, 'html.parser')

    htmlc.convert_mp4_to_link(tag)

    assert tag.decode_contents()=="""<div><a href="srclink"></a><source src="srclink" type="video/mp4"/></div>"""


def test_convert_iframes_to_link() -> None:
    initial_string = """<iframe src="iframesrc" data-embed-src="iframedatasrc"></iframe><iframe src="iframesrc"></iframe>"""
    soup = BeautifulSoup(initial_string, 'html.parser')

    htmlc.convert_iframes_to_link(soup)

    assert soup.decode_contents()=="""<a>iframedatasrc</a><a>iframesrc</a>"""

def test_process_spoiler() -> None:
    initial_string = '<div class="ipsSpoiler"><p>I\'m a spoiler</p></div>'

    soup = BeautifulSoup(initial_string, 'html.parser')

    htmlc.process_spoiler(soup)

    assert(soup.decode_contents()=='<div class="ipsSpoiler"><p>&gt;!I\'m a spoiler!&lt;</p></div>')

def test_process_spoiler2() -> None:
    initial_string = '<div class="ipsSpoiler"><ul><li>Item1</li><li>Item2</li></ul></div>'

    soup = BeautifulSoup(initial_string, 'html.parser')
    htmlc.process_spoiler(soup)

    assert soup.decode_contents()=='<div class="ipsSpoiler"><p>&gt;!Item1!&lt;</p><p>&gt;!Item2!&lt;</p></div>'

def test_process_tables() -> None:
    initial_string = """
	<table><tbody><tr>
			<td>
				<p>Test</p>
				<p>
					<strong>Tactical</strong>
				</p>
			</td>
			<td>
				<p>
					<strong>Piloting<br>Test</strong>
				</p>
			</td>
			<td>
				<p>
					<strong>Gunnery</strong>
				</p>
			</td>
			<td>
				<p>
					<strong>&nbsp;</strong>
				</p>
			</td>
		</tr></tbody></table>
	""".replace("\t","").replace("\n","")

    Expected = """
		<table><tbody><tr>
			<td>
				TestTactical
			</td>
			<td>
				PilotingTest
			</td>
			<td>
				Gunnery
			</td>
			<td>-</td>
		</tr></tbody></table>
	""".replace("\t","").replace("\n","")


    soup = BeautifulSoup(initial_string, 'html.parser')

    htmlc.process_tables(soup)

    assert soup.decode_contents()==Expected


def test_decompose_all_span_should_unwrap_spans() -> None:
    initial_string = "<p>Text <span>in span</span> more text</p>"
    
    desired_result = "<p>Text in span more text</p>"
    
    soup = BeautifulSoup(initial_string, 'html.parser')
    htmlc.decompose_all_span(soup)
    
    assert soup.decode_contents() == desired_result


def test_decompose_all_span_should_handle_multiple_spans() -> None:
    initial_string = "<div><span>First</span> <span>Second</span> <span>Third</span></div>"
    
    desired_result = "<div>First Second Third</div>"
    
    soup = BeautifulSoup(initial_string, 'html.parser')
    htmlc.decompose_all_span(soup)
    
    assert soup.decode_contents() == desired_result


def test_decompose_all_b_should_unwrap_b_tags() -> None:
    initial_string = "<p>Text <b>in bold</b> more text</p>"
    
    desired_result = "<p>Text in bold more text</p>"
    
    soup = BeautifulSoup(initial_string, 'html.parser')
    htmlc.decompose_all_b(soup)
    
    assert soup.decode_contents() == desired_result


def test_decompose_all_b_should_handle_multiple_b_tags() -> None:
    initial_string = "<div><b>Bold1</b> text <b>Bold2</b></div>"
    
    desired_result = "<div>Bold1 text Bold2</div>"
    
    soup = BeautifulSoup(initial_string, 'html.parser')
    htmlc.decompose_all_b(soup)
    
    assert soup.decode_contents() == desired_result


def test_decompose_all_em_should_add_underscores() -> None:
    initial_string = "<em>test1</em>"
    
    desired_result = "_test1_"
    
    soup = BeautifulSoup(initial_string, 'html.parser')
    htmlc.decompose_all_em(soup)
    
    assert soup.decode_contents() == desired_result


def test_decompose_all_em_should_keep_spaces() -> None:
    initial_string = " <em> test1 </em> "
    
    desired_result = "  _test1_  "
    
    soup = BeautifulSoup(initial_string, 'html.parser')
    htmlc.decompose_all_em(soup)
    
    assert soup.decode_contents() == desired_result


def test_decompose_all_em_should_handle_empty_em() -> None:
    initial_string = "<p>Text <em>   </em> more</p>"
    
    soup = BeautifulSoup(initial_string, 'html.parser')
    htmlc.decompose_all_em(soup)
    
    # Empty em tags should be unwrapped without markdown
    assert soup.find("em") is None


def test_decompose_all_table_cell_children_should_unwrap_nested_tags() -> None:
    initial_string = "<td><p>Test <strong>content</strong></p></td>"
    
    soup = BeautifulSoup(initial_string, 'html.parser')
    table_cell = soup.find("td")
    assert table_cell is not None
    
    htmlc.decompose_all_table_cell_children(table_cell)
    
    # All nested tags should be unwrapped, leaving only text
    assert table_cell.decode_contents() == "Test content"


def test_decompose_all_table_cell_children_should_preserve_text() -> None:
    initial_string = "<td><span>Keep</span> <strong>this</strong> <em>text</em></td>"
    
    soup = BeautifulSoup(initial_string, 'html.parser')
    table_cell = soup.find("td")
    
    assert table_cell is not None
    htmlc.decompose_all_table_cell_children(table_cell)
    
    assert table_cell.decode_contents() == "Keep this text"


def test_replace_empty_table_cell_content_with_dash_should_replace_empty_cell() -> None:
    initial_string = "<td>   </td>"
    
    soup = BeautifulSoup(initial_string, 'html.parser')
    table_cell = soup.find("td")
    
    assert table_cell is not None
    htmlc.replace_empty_table_cell_content_with_dash(table_cell)
    
    assert table_cell.decode_contents() == "-"


def test_replace_empty_table_cell_content_with_dash_should_not_replace_non_empty_cell() -> None:
    initial_string = "<td>Content</td>"
    
    soup = BeautifulSoup(initial_string, 'html.parser')
    table_cell = soup.find("td")
    
    assert table_cell is not None
    htmlc.replace_empty_table_cell_content_with_dash(table_cell)
    
    assert table_cell.decode_contents() == "Content"


def test_process_nested_lists_should_not_exceed_max_depth() -> None:
    # Create a deeply nested list (4 levels deep)
    initial_string = "<ul><li>L1<ul><li>L2<ul><li>L3<ul><li>L4</li></ul></li></ul></li></ul></li></ul>"
    
    soup = BeautifulSoup(initial_string, 'html.parser')
    htmlc.process_nested_lists(soup, max_depth=3)
    
    # L4 should be converted to use a caret instead of being nested
    contents = soup.decode_contents()
    # The L4 item should have been unwrapped and replaced with a caret
    assert "‣" in contents


def test_process_nested_lists_should_preserve_shallow_nesting() -> None:
    initial_string = "<ul><li>L1<ul><li>L2</li></ul></li></ul>"
    
    soup = BeautifulSoup(initial_string, 'html.parser')
    htmlc.process_nested_lists(soup, max_depth=3)
    
    # Shallow nesting should remain as nested lists
    assert soup.find("ul") is not None
    assert soup.find("li") is not None


def test_process_nested_lists_single_level_should_remain_unchanged() -> None:
    initial_string = "<ul><li>Item 1</li><li>Item 2</li></ul>"
    
    soup = BeautifulSoup(initial_string, 'html.parser')
    htmlc.process_nested_lists(soup, max_depth=3)
    
    # Single level lists should remain unchanged
    assert len(soup.find_all("ul")) == 1
    assert len(soup.find_all("li")) == 2


def test_process_html_tag_should_call_all_processing_functions() -> None:
    # Create HTML with multiple elements that need processing
    initial_string = """
    <div>
        <blockquote><div>Header</div><p>Content</p></blockquote>
        <p>Text with <b>bold</b> and <em>emphasis</em> and <span>span</span></p>
        <table><tr><td><p>Cell</p></td><td></td></tr></table>
        <div class="ipsSpoiler"><p>Secret</p></div>
    </div>
    """
    
    soup = BeautifulSoup(initial_string, 'html.parser')
    htmlc.process_html_tag(soup)
    
    # Verify that various processing occurred:
    # - Span tags should be gone
    assert soup.find("span") is None
    # - b tags should be gone
    assert soup.find("b") is None
    # - Spoilers should have processed content
    spoiler = soup.find("div", {"class": "ipsSpoiler"})
    if spoiler:
        assert "!" in spoiler.decode_contents()