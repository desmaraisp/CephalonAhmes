import src.HTMLCorrections as htmlc
from bs4 import BeautifulSoup
import html


def test_decompose_all_blockquote_headers() -> None:
    InitialString = """<blockquote><div>HeaderContent</div><div>StringContent</div></blockquote>"""

    DesiredResult = """<blockquote><div>StringContent</div></blockquote>"""

    tag = BeautifulSoup(InitialString, 'html.parser')

    htmlc.decompose_all_blockquote_headers(tag)

    assert tag.decode_contents()== DesiredResult

def test_strip_tabs_and_spaces_but_keep_newlines() -> None:
    InitialString = """  
			  
	 
	   test1 test2 
	   
			   
	   test3  
		    
	   """

    DesiredResult = """


test1 test2 
	   
			   
	   test3

"""


    Result = htmlc.strip_heading_or_trailing_tabs_and_spaces_but_keep_newlines(InitialString)

    assert Result== DesiredResult


def test_strip_Spoiler_Header() -> None:
    InitialString = """<div class="ipsSpoiler"><div class="ipsSpoiler_header">HeaderContents</div><div class="ipsSpoiler_contents">SpoilerContents</div></div>"""
    tag = BeautifulSoup(InitialString, 'html.parser')

    htmlc.decompose_all_spoiler_headers(tag)

    assert tag.decode_contents()=="""<div class="ipsSpoiler"><div class="ipsSpoiler_contents">SpoilerContents</div></div>"""

def test_strip_Edited_Footer() -> None:
    InitialString = """<span class="ipsType_reset ipsType_medium ipsType_light"><strong>Edited by TestUser</strong></span>"""
    tag = BeautifulSoup(InitialString, 'html.parser')

    htmlc.decompose_all_edited_on_footers(tag)

    assert tag.decode_contents()==""

def test_strip_image_links_to_avoid_double_links() -> None:
    InitialString = """<a href="hreflink"><img src="imgsource"></a>"""
    tag = BeautifulSoup(InitialString, 'html.parser')

    htmlc.strip_image_links_to_avoid_double_links(tag)

    assert tag.decode_contents()=="""<a href><img src="hreflink"/></a>"""

def test_strip_image_links_to_avoid_double_links2() -> None:
    InitialString = """<a href="hreflink"><div><img src="imgsource"></div></a>"""
    tag = BeautifulSoup(InitialString, 'html.parser')

    htmlc.strip_image_links_to_avoid_double_links(tag)

    assert tag.decode_contents()=="""<a href><div><img src="hreflink"/></div></a>"""

def test_convert_mp4_to_link() -> None:
    InitialString = """<div><a href="SomeRandomHref"/><source type="video/mp4" src="srclink"/></div>"""
    tag = BeautifulSoup(InitialString, 'html.parser')

    htmlc.convert_mp4_to_link(tag)

    assert tag.decode_contents()=="""<div><a href="srclink"></a><source src="srclink" type="video/mp4"/></div>"""


def test_eliminate_and_propagate_tag() -> None:
    InitialString = """<div><strong>String1<a>String2</a>String3</strong><div><strong>String4<a>String5</a></strong></div></div>"""
    soup = BeautifulSoup(InitialString, 'html.parser')

    htmlc.eliminate_and_propagate_tag(soup, "strong")

    assert soup.decode_contents()=="""
		<div>
			<span>
				<strong>String1</strong>
				<a><strong>String2</strong></a>
				<strong>String3</strong>
			</span>
			<div>
				<span>
					<strong>String4</strong>
					<a><strong>String5</strong></a>
				</span>
			</div>
		</div>
	""".replace("\t","").replace("\n","")


def test_convert_iframes_to_link() -> None:
    InitialString = """<iframe src="iframesrc" data-embed-src="iframedatasrc"></iframe><iframe src="iframesrc"></iframe>"""
    soup = BeautifulSoup(InitialString, 'html.parser')

    htmlc.convert_iframes_to_link(soup)

    assert soup.decode_contents()=="""<a>iframedatasrc</a><a>iframesrc</a>"""

def test_add_spoiler_tag_to_html_element() -> None:
    InitialString = """
		<span>
			<div class="ipsSpoiler">test</div>
		</span>
	""".replace("\t","").replace("\n","")

    soup = BeautifulSoup(InitialString, 'html.parser')

    htmlc.add_spoiler_tag_to_html_element(soup.find('div', recursive=True), soup)


    assert html.unescape(soup.decode_contents())=="""
		<span>
			<div class="ipsSpoiler">>!test</div>
		</span>
	""".replace("\t","").replace("\n","")


def test_Process_Spoiler() -> None:
    InitialString = """
		<span>
			<div class="ipsSpoiler"> String1<strong>String2</strong><br/> String3</div>
		</span>
	""".replace("\t","").replace("\n","")

    soup = BeautifulSoup(InitialString, 'html.parser')

    htmlc.Process_Spoiler(soup)

    assert html.unescape(soup.decode_contents())=="""
		<span>
			<div class="ipsSpoiler">>! String1<strong>String2</strong> String3</div>
		</span>
	""".replace("\t","").replace("\n","")

def test_Process_Spoiler2() -> None:
    InitialString = """
		<span>
			<div class="ipsSpoiler">
				<ul>
					<li>Item1</li>
					<li>Item2</li>
				</ul>
			</div>
		</span>
	""".replace("\t","").replace("\n","")

    soup = BeautifulSoup(InitialString, 'html.parser')

    htmlc.Process_Spoiler(soup)

    assert html.unescape(soup.decode_contents())=="""
		<span>
			<div class="ipsSpoiler">
				<ul>
					<span>>!<li>Item1</li></span>
					<span>>!<li>Item2</li></span>
				</ul>
			</div>
		</span>
	""".replace("\t","").replace("\n","")

def test_Process_Tables() -> None:
    InitialString = """
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


    soup = BeautifulSoup(InitialString, 'html.parser')

    htmlc.process_tables(soup)

    assert soup.decode_contents()==Expected