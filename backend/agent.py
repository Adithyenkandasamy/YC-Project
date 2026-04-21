from typing import Dict, List

from llm import generate_answer
from scraper import scrape_urls
from search import search_web


async def run_agent(query: str) -> Dict:
    search_results = search_web(query, max_results=5)
    if not search_results:
        return {"answer": "I don't know", "sources": []}

    links = [item["link"] for item in search_results[:5]]
    scraped_map = await scrape_urls(links)

    scraped_sources: List[Dict[str, str]] = []
    for item in search_results[:5]:
        content = scraped_map.get(item["link"], "")
        if content:
            scraped_sources.append({**item, "content": content})

    answer = generate_answer(query, scraped_sources)

    return {
        "answer": answer,
        "sources": [{"title": source["title"], "link": source["link"]} for source in search_results[:5]],
    }
