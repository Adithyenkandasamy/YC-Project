import asyncio
import time
from typing import Dict, List

import aiohttp
from bs4 import BeautifulSoup

_SCRAPE_CACHE: Dict[str, Dict] = {}
_CACHE_TTL_SECONDS = 600
_MAX_CHARS = 2000
_MAX_RETRIES = 2



def _get_cached(url: str):
    cached = _SCRAPE_CACHE.get(url)
    if not cached:
        return None
    if time.time() - cached["timestamp"] > _CACHE_TTL_SECONDS:
        _SCRAPE_CACHE.pop(url, None)
        return None
    return cached["content"]



def _clean_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "noscript"]):
        tag.decompose()

    paragraphs: List[str] = []
    for p in soup.find_all("p"):
        text = p.get_text(" ", strip=True)
        if len(text) > 30:
            paragraphs.append(text)

    content = "\n".join(paragraphs)
    return content[:_MAX_CHARS]


async def _fetch_one(session: aiohttp.ClientSession, url: str) -> str:
    cached = _get_cached(url)
    if cached is not None:
        return cached

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
    }

    for attempt in range(_MAX_RETRIES + 1):
        try:
            async with session.get(url, headers=headers, timeout=12) as response:
                if response.status >= 400:
                    raise aiohttp.ClientError(f"HTTP {response.status}")
                html = await response.text(errors="ignore")
                cleaned = _clean_text(html)
                _SCRAPE_CACHE[url] = {"timestamp": time.time(), "content": cleaned}
                return cleaned
        except (aiohttp.ClientError, asyncio.TimeoutError):
            if attempt == _MAX_RETRIES:
                return ""
            await asyncio.sleep(0.5 * (attempt + 1))

    return ""


async def scrape_urls(urls: List[str]) -> Dict[str, str]:
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [_fetch_one(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    output: Dict[str, str] = {}
    for url, value in zip(urls, results):
        if isinstance(value, Exception):
            output[url] = ""
        else:
            output[url] = value
    return output
