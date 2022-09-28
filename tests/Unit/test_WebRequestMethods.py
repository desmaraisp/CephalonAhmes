import httpretty, pytest, requests
from src import (
    WebRequestMethods as wrm,
)

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

