import requests
from requests.adapters import HTTPAdapter, Retry
from fake_useragent import UserAgent

ua = UserAgent(fallback='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36')

def get_response_from_generic_url(url: str, MaxRetries: int = 5) -> requests.Response:
    session = requests.Session()

    retries = Retry(total=MaxRetries,
                    backoff_factor=0.1,
                    status_forcelist=[ 500, 502, 503, 504 ],
                    raise_on_status=True,
                )

    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))

    headers={
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        "Pragma": "no-cache, no-store, must-revalidate",
        'User-Agent': ua.random,
        'referer': "https://google.com"
    }
    
    try:
        return session.get(url, timeout=20, headers=headers)
    except Exception as e:
        raise Exception("HTTP failure for '{}'.".format(url)) from e

