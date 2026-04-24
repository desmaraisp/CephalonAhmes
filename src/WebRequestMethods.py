import requests
from requests.adapters import HTTPAdapter, Retry

def get_response_from_generic_url(url: str, max_retries: int = 5, timeout: float = 20) -> requests.Response:
    session = requests.Session()

    retries = Retry(total=max_retries,
                    backoff_factor=0.1,
                    status_forcelist=[ 500, 502, 503, 504 ],
                    raise_on_status=True,
                )

    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session.get(url, timeout=timeout)

