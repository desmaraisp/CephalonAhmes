import selenium.common.exceptions as sce
import httpretty, pytest, requests, func_timeout
from src import (
    WebRequestMethods as wrm,
    SeleniumUtilities as selu
)
from pytest_localserver.http import WSGIServer

@httpretty.activate
def test_get_response_from_generic_url_success():
    httpretty.register_uri(httpretty.GET, 'http://test.com/', status=200)
    response_text = (wrm.get_response_from_generic_url('http://test.com/')).text
        
    assert(response_text =='{"message": "HTTPretty :)"}')

@httpretty.activate
def test_get_response_from_generic_url_500():
    httpretty.register_uri(httpretty.GET, 'http://test.com/', status=500)
    
    with pytest.raises(Exception, match="HTTP failure for 'http://test.com/'") as e:
        wrm.get_response_from_generic_url('http://test.com/', 1)

@httpretty.activate
def test_get_response_from_generic_url_timeout():
    global exception_count
    exception_count = 0
    
    def exceptionCallback(request, uri, headers):
        global exception_count
        exception_count +=1
        raise requests.Timeout('Connection successfully timed out.')
    
    httpretty.register_uri(httpretty.GET, 'http://test.com/', status=200, body=exceptionCallback)
    
    with pytest.raises(Exception, match="HTTP failure for 'http://test.com/'") as e:
        wrm.get_response_from_generic_url('http://test.com/', 2)
    
    assert(exception_count == 3)

@pytest.fixture
def setup_webdriver():
    browser = selu.start_chrome_browser()
    yield browser
    browser.quit()

def simple_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/html')]
    start_response(status, response_headers)
    return [b'<time>test</time>']


@pytest.fixture
def testserver():
    server = WSGIServer(application=simple_app)
    server.start()
    yield server
    server.stop()


def test_browser_fetch_updated_forum_page_source_safely_success(setup_webdriver, mocker, testserver):
    mocker.patch("src.WebRequestMethods.navigate_to_force_data_reload")

    response_text = wrm.browser_fetch_updated_forum_page_source_safely(testserver.url, setup_webdriver, 1)
    
    assert('test' in response_text)

def test_browser_fetch_updated_forum_page_source_safely_500(setup_webdriver, mocker, httpserver):
    httpserver.serve_content("test", 500)
    mocked = mocker.patch("src.WebRequestMethods.check_page_success", side_effect = wrm.check_page_success)

    with pytest.raises(sce.NoSuchElementException) as e:
        wrm.browser_fetch_updated_forum_page_source_safely(httpserver.url, setup_webdriver, 2)
    assert(mocked.call_count == 2)
        
def test_browser_fetch_updated_forum_page_source_safely_timeout(setup_webdriver, mocker, httpserver):
    httpserver.serve_content("test", 200)
    mocked = mocker.patch("src.WebRequestMethods.fetch_timeout_wrapper", side_effect=func_timeout.exceptions.FunctionTimedOut())

    with pytest.raises(func_timeout.exceptions.FunctionTimedOut) as e:
        wrm.browser_fetch_updated_forum_page_source_safely(httpserver.url, setup_webdriver, 2)
    
    assert(mocked.call_count == 2)
