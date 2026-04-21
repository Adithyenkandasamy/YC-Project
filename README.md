# AI Answer Engine (Groq + FastAPI + React)

A portfolio-ready AI-powered answer engine that fetches live web results, scrapes source content, and produces citation-grounded answers using Groq.

## Folder Structure

```bash
YC-Project/
├── backend/
│   ├── agent.py
│   ├── llm.py
│   ├── main.py
│   ├── scraper.py
│   ├── search.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.css
    │   ├── App.jsx
    │   ├── index.css
    │   └── main.jsx
    ├── package.json
    └── ...
```

## Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create environment variable:

```bash
export GROQ_API_KEY="your_groq_api_key"
```

Run backend:

```bash
uvicorn main:app --reload --port 8000
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Optional API URL override:

```bash
export VITE_API_BASE_URL="http://localhost:8000"
```

## API

### `POST /ask`

Request:

```json
{
  "query": "What is Dijkstra's Algorithm?"
}
```

Response:

```json
{
  "answer": "... [1] ...",
  "sources": [
    {"title": "...", "link": "..."}
  ]
}
```

### `GET /ask?query=...`

Also supported.

## Agent Workflow

1. Receive user query
2. Search live web using DuckDuckGo HTML
3. Select top results
4. Async scrape page paragraph text with retries
5. Combine source context
6. Query Groq (`llama3-70b-8192`, temperature `0.3`)
7. Return concise answer with citations and source links

## Test Case

Use query:

`What is Dijkstra's Algorithm?`

Expected behavior:
- Returns direct explanation
- Includes citation markers like `[1]`, `[2]`
- Displays clickable sources in frontend
