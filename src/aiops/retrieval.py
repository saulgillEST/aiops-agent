import re
import requests

url_re = re.compile(r'(https?://[^\s,]+)')

def fetch_urls_from_text(text: str):
    return url_re.findall(text)

def fetch_text(url: str, timeout=15):
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.text