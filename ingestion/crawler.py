import requests
from bs4 import BeautifulSoup

def fetch_page(url: str) -> str:
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # TODO: tune which tags to keep
    texts = [t.get_text(" ", strip=True) for t in soup.find_all(["h1","h2","p","li"])]
    return "\n".join(texts)
