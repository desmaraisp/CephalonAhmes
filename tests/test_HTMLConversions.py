import src.Warframe_patchnotes_thief_script as wpts
from bs4 import BeautifulSoup


def test_add_multiline_spoiler_tag_if_multiple_line_returns_in_a_row():
	Initial_String = "\n I am a first paragraph. \n \n I am a second paragraph that needs a spoiler tag. \n I am a third paragraph that does not need a tag, before or after. \n\n"
	Processed_string = wpts.add_multiline_spoiler_tag_if_multiple_line_returns_in_a_row(Initial_String)
	assert Processed_string == "I am a first paragraph.\n\n>!I am a second paragraph that needs a spoiler tag. \n I am a third paragraph that does not need a tag, before or after."
	

def test_strip_BlockQuote_Header():
	InitialString = """
		<blockquote>
			<div>HeaderContent</div>
			<div>StringContent</div>
		</blockquote>
	"""
	
	DesiredResult = """
		<blockquote>
			<div>StringContent</div>
		</blockquote>
	"""
	
	tag = BeautifulSoup(InitialString, 'html.parser')

	wpts.HTML_Corrections.strip_BlockQuote_Header(tag)
	
	assert tag.decode_contents().replace("\n", "") == BeautifulSoup(DesiredResult, 'html.parser').decode_contents().replace("\n", "")

	
	
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
	
	assert soup.decode_contents()=="""<div><div><strong>String1</strong><a><strong>String2</strong></a><strong>String3</strong></div><div><div><strong>String4</strong><a><strong>String5</strong></a></div></div></div>"""
