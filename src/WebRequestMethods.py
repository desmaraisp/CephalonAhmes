import requests
from requests.adapters import HTTPAdapter, Retry

def get_response_from_generic_url(url: str, MaxRetries: int = 5) -> requests.Response:
    session = requests.Session()

    retries = Retry(total=MaxRetries,
                    backoff_factor=0.1,
                    status_forcelist=[ 500, 502, 503, 504 ],
                    raise_on_status=True,
                )

    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.cookies.set("gid", value="59aec12f3ade7fd1f103decf", domain="forums.warframe.com", path="/") # type: ignore
    session.cookies.set("ips4_noCache", value="1", domain="forums.warframe.com", path="/") # type: ignore
    
    try:
        return session.get(url, timeout=20)
    except Exception as e:
        raise Exception("HTTP failure for '{}'.".format(url)) from e

