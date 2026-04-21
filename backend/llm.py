import json
import os
from typing import Dict, List

import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
SYSTEM_PROMPT = """You are an AI research assistant.

* Answer using ONLY the provided sources
* Do NOT hallucinate
* If information is insufficient, say 'I don't know'
* Cite sources using [1], [2], etc.
* Keep answers clear, structured, and concise"""



def _format_sources(scraped_sources: List[Dict[str, str]]) -> str:
    formatted = []
    for idx, source in enumerate(scraped_sources, start=1):
        formatted.append(
            f"[{idx}] Title: {source['title']}\n"
            f"URL: {source['link']}\n"
            f"Content:\n{source['content'] or '[No content extracted]'}"
        )
    return "\n\n".join(formatted)



def generate_answer(query: str, scraped_sources: List[Dict[str, str]]) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")

    if not scraped_sources:
        return "I don't know"

    source_context = _format_sources(scraped_sources)
    user_prompt = (
        f"Question: {query}\n\n"
        f"Sources:\n{source_context}\n\n"
        "Provide a direct answer with citations like [1], [2]."
    )

    payload = {
        "model": "llama3-70b-8192",
        "temperature": 0.3,
        "max_tokens": 512,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = requests.post(GROQ_API_URL, headers=headers, data=json.dumps(payload), timeout=20)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()
