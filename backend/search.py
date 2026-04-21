import time
from typing import Dict, List
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

_SEARCH_CACHE: Dict[str, Dict] = {}
_CACHE_TTL_SECONDS = 300
_DDG_HTML_URL = "https://html.duckduckgo.com/html/"



def _get_cached(query: str):
    cached = _SEARCH_CACHE.get(query)
    if not cached:
        return None
    if time.time() - cached["timestamp"] > _CACHE_TTL_SECONDS:
        _SEARCH_CACHE.pop(query, None)
        return None
    return cached["results"]



def search_web(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    cached = _get_cached(query)
    if cached is not None:
        return cached

    params = {"q": query}
    url = f"{_DDG_HTML_URL}?{urlencode(params)}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    results: List[Dict[str, str]] = []

    for anchor in soup.select("a.result__a"):
        title = anchor.get_text(" ", strip=True)
        link = anchor.get("href")
        if not title or not link:
            continue
        results.append({"title": title, "link": link})
        if len(results) >= max_results:
            break

    _SEARCH_CACHE[query] = {"timestamp": time.time(), "results": results}
    return results
