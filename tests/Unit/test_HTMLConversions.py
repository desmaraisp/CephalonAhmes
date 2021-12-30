import src.Warframe_patchnotes_thief_script as wpts
from bs4 import BeautifulSoup
import html


def test_strip_BlockQuote_Header():
	InitialString = """<blockquote><div>HeaderContent</div><div>StringContent</div></blockquote>"""
	
	DesiredResult = """<blockquote><div>StringContent</div></blockquote>"""
	
	tag = BeautifulSoup(InitialString, 'html.parser')

	wpts.HTML_Corrections.strip_BlockQuote_Header(tag)
	
	assert tag.decode_contents()== DesiredResult

	
	
def test_strip_Spoiler_Header():
	InitialString = """<div class="ipsSpoiler"><div class="ipsSpoiler_header">HeaderContents</div><div class="ipsSpoiler_contents">SpoilerContents</div></div>"""
	tag = BeautifulSoup(InitialString, 'html.parser')

	wpts.HTML_Corrections.strip_Spoiler_Header(tag)
	
	assert tag.decode_contents()=="""<div class="ipsSpoiler"><div class="ipsSpoiler_contents">SpoilerContents</div></div>"""

def test_strip_Edited_Footer():
	InitialString = """<span class="ipsType_reset ipsType_medium ipsType_light"><strong>Edited by TestUser</strong></span>"""
	tag = BeautifulSoup(InitialString, 'html.parser')

	wpts.HTML_Corrections.strip_Edited_Footer(tag)
	
	assert tag.decode_contents()==""
	
def test_strip_image_links_to_avoid_double_links():
	InitialString = """<a href="hreflink"><img src="imgsource"></a>"""
	tag = BeautifulSoup(InitialString, 'html.parser')

	wpts.HTML_Corrections.strip_image_links_to_avoid_double_links(tag)
	
	assert tag.decode_contents()=="""<a href><img src="hreflink"/></a>"""

def test_strip_image_links_to_avoid_double_links2():
	InitialString = """<a href="hreflink"><div><img src="imgsource"></div></a>"""
	tag = BeautifulSoup(InitialString, 'html.parser')

	wpts.HTML_Corrections.strip_image_links_to_avoid_double_links(tag)
	
	assert tag.decode_contents()=="""<a href><div><img src="hreflink"/></div></a>"""

def test_convert_mp4_to_link():
	InitialString = """<div><a href="SomeRandomHref"/><source type="video/mp4" src="srclink"/></div>"""
	tag = BeautifulSoup(InitialString, 'html.parser')

	wpts.HTML_Corrections.convert_mp4_to_link(tag)
	
	assert tag.decode_contents()=="""<div><a href="srclink"></a><source src="srclink" type="video/mp4"/></div>"""

def test_recursive_function():
	InitialString = """<strong>String1<a>String2</a>String3</strong>"""
	soup = BeautifulSoup(InitialString, 'html.parser')
	
	wpts.HTML_Corrections.recursive_function(soup.strong, "strong", soup)
	
	assert soup.decode_contents()=="""<div><strong>String1</strong><a><strong>String2</strong></a><strong>String3</strong></div>"""


def test_eliminate_and_propagate_tag():
	InitialString = """<div><strong>String1<a>String2</a>String3</strong><div><strong>String4<a>String5</a></strong></div></div>"""
	soup = BeautifulSoup(InitialString, 'html.parser')
	
	wpts.HTML_Corrections.eliminate_and_propagate_tag(soup, "strong", soup)
	
	assert soup.decode_contents()=="""
		<div>
			<div>
				<strong>String1</strong>
				<a><strong>String2</strong></a>
				<strong>String3</strong>
			</div>
			<div>
				<div>
					<strong>String4</strong>
					<a><strong>String5</strong></a>
				</div>
			</div>
		</div>
	""".replace("\t","").replace("\n","")


def test_convert_iframes_to_link():
	InitialString = """<iframe src="iframesrc"></iframe>"""
	soup = BeautifulSoup(InitialString, 'html.parser')
	
	wpts.HTML_Corrections.convert_iframes_to_link(soup, soup)
	
	assert soup.decode_contents()=="""<a>iframesrc</a>"""

def test_add_spoiler_tag_to_html_element():
	InitialString = """
		<span>
			<div class="ipsSpoiler">test</div>
		</span>
	""".replace("\t","").replace("\n","")
	
	soup = BeautifulSoup(InitialString, 'html.parser')
	
	wpts.add_spoiler_tag_to_html_element(soup.span.div, soup)

	
	assert html.unescape(soup.decode_contents())=="""
		<span>
			<div>
				>!
				<div class="ipsSpoiler">test</div>
			</div>
		</span>
	""".replace("\t","").replace("\n","")


def test_Process_Spoiler():
	InitialString = """
		<span>
			<div class="ipsSpoiler"> String1<strong>String2</strong><br/> String3</div>
		</span>
	""".replace("\t","").replace("\n","")
	
	soup = BeautifulSoup(InitialString, 'html.parser')
	
	wpts.HTML_Corrections.Process_Spoiler(soup)
	
	assert html.unescape(soup.decode_contents())=="""
		<span>
			<div>
				>!
				<div class="ipsSpoiler"> String1<strong>String2</strong> String3</div>
			</div>
		</span>
	""".replace("\t","").replace("\n","")

def test_Process_Spoiler2():
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
	
	wpts.HTML_Corrections.Process_Spoiler(soup)
	
	assert html.unescape(soup.decode_contents())=="""
		<span>
			<div class="ipsSpoiler">
				<ul>
					<div>>!<li>Item1</li></div>
					<div>>!<li>Item2</li></div>
				</ul>
			</div>
		</span>
	""".replace("\t","").replace("\n","")

def test_Process_Tables():
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
	
	wpts.HTML_Corrections.Process_Tables(soup)
	
	assert soup.decode_contents()==Expected