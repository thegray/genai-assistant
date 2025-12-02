# ingestion/link_discovery.py
from typing import List, Set, Deque, Tuple
from collections import deque
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


def is_internal_link(url: str, base_domain: str = "axrail.ai") -> bool:
    parsed = urlparse(url)
    netloc = parsed.netloc

    if not netloc:
        # relative URL => internal
        return True

    # treat any subdomain under axrail.ai as internal
    return netloc.endswith(base_domain)


def clean_url(url: str) -> str:
    # remove fragments (#...) and trailing slashes
    parsed = urlparse(url)
    # drop fragment and query if needed
    parsed = parsed._replace(fragment="", query="")
    cleaned = parsed.geturl()
    # normalize trailing slash a bit
    if cleaned.endswith("/") and cleaned != parsed.scheme + "://" + parsed.netloc + "/":
        cleaned = cleaned.rstrip("/")
    return cleaned


def discover_internal_links(
    start_urls: List[str],
    max_depth: int = 2,
    max_pages: int = 50,
    timeout: int = 10,
) -> List[str]:
    """
    breadth-first crawl starting from start_urls, limited by depth and page count.
    returns list of discovered internal URLs, including start URLs.
    """
    # if not start_urls:
    #     return []
    # base_netloc = urlparse(start_urls[0]).netloc

    # hardcoded since only for this site
    base_domain = "axrail.ai"

    visited: Set[str] = set()
    result: List[str] = []

    # queue items: (url, depth)
    queue: Deque[Tuple[str, int]] = deque()

    for u in start_urls:
        u_clean = clean_url(u)
        queue.append((u_clean, 0))

    while queue and len(result) < max_pages:
        url, depth = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        result.append(url)

        if depth >= max_depth:
            continue

        try:
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
        except Exception as e:
            print(f"exception on requests: {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            # print("FOUND HREF:", href)

            if not href or href.startswith("#") or href.startswith("mailto:"):
                continue

            absolute = urljoin(url, href)
            if not is_internal_link(absolute, base_domain):
                continue

            next_url = clean_url(absolute)
            if next_url not in visited:
                queue.append((next_url, depth + 1))

    return result
