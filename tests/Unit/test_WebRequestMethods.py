from typing import Any, Generator
import httpretty, pytest, requests
from src import (
    WebRequestMethods as wrm,
)

@pytest.fixture
def http_pretty_activate() -> Generator[None, None, None]:
    httpretty.enable(verbose=True, allow_net_connect=False)
    
    yield
    
    httpretty.disable()
    httpretty.reset() 

def test_get_response_from_generic_url_success(http_pretty_activate: None) -> None:
    httpretty.register_uri(httpretty.GET, 'http://test.com/', status=200)
    response_text = (wrm.get_response_from_generic_url('http://test.com/')).text
        
    assert(response_text =='{"message": "HTTPretty :)"}')

def test_get_response_from_generic_url_500(http_pretty_activate: None) -> None:
    httpretty.register_uri(httpretty.GET, 'http://test.com/', status=500)
    
    with pytest.raises(Exception, match="HTTP failure for 'http://test.com/'") as e:
        wrm.get_response_from_generic_url('http://test.com/', 1)

class Exception_Callback_Generator:
    count:int = 0

    def trigger(self, _: Any, __: Any, ___: Any) -> None:
        self.count+=1
        raise requests.Timeout('Connection successfully timed out.')

def test_get_response_from_generic_url_timeout(http_pretty_activate: None) -> None:
    callback_generator = Exception_Callback_Generator()
    httpretty.register_uri(httpretty.GET, 'http://test.com/', status=200, body=callback_generator.trigger)
    
    with pytest.raises(Exception, match="HTTP failure for 'http://test.com/'") as e:
        wrm.get_response_from_generic_url('http://test.com/', 2)
    
    assert(callback_generator.count == 3)

