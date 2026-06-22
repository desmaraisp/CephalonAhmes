import threading
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from requests.exceptions import RetryError
import pytest, responses
from responses import registries
from src import (
    WebRequestMethods as wrm,
)


@responses.activate
def test_get_response_from_generic_url_success() -> None:
    responses.add(responses.GET, 'https://test.com/', body='{"message": "HTTPretty :)"}', status=200)
    response_text = (wrm.get_response_from_generic_url('https://test.com/')).text
    assert response_text == '{"message": "HTTPretty :)"}'


@responses.activate
def test_get_response_from_generic_url_500() -> None:
    responses.add(responses.GET, 'https://test.com/', status=500)
    with pytest.raises(RetryError):
        wrm.get_response_from_generic_url('https://test.com/', 1)

class SlowHandler(BaseHTTPRequestHandler):
    is_called = False
    def do_GET(self):
        try:
            if(SlowHandler.is_called):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Second response")
                return

            SlowHandler.is_called = True
            import time
            time.sleep(1)  # Deliberately longer than the client timeout
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Delayed response")
        except Exception:
            pass

def run_server(server):
    server.serve_forever()

def test_get_response_from_generic_url_timeout() -> None:
    # Find a free port
    sock = socket.socket()
    sock.bind(('localhost', 0))
    port = sock.getsockname()[1]
    sock.close()
    server = HTTPServer(('localhost', port), SlowHandler)
    thread = threading.Thread(target=run_server, args=(server,), daemon=True)
    thread.start()
    url = f'http://localhost:{port}/'
    try:
        response = wrm.get_response_from_generic_url(url, 3, 0.5)
        assert response.status_code == 200
        assert response.text == "Second response"
    finally:
        server.shutdown()
        thread.join(timeout=1)

@responses.activate(registry=registries.OrderedRegistry)
def test_max_retries():
    url = "https://example.com"
    rsp1 = responses.get(url, body="Error", status=500)
    rsp3 = responses.get(url, body="Error", status=500)
    rsp4 = responses.get(url, body="Error", status=500)

    with pytest.raises(RetryError):
        wrm.get_response_from_generic_url(url, 2)

    assert rsp1.call_count == 1
    assert rsp3.call_count == 1
    assert rsp4.call_count == 1
