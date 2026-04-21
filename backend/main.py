from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent import run_agent

app = FastAPI(title="AI Answer Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    query: str = Field(min_length=2)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/ask")
async def ask_get(query: str):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        return await run_agent(query.strip())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/ask")
async def ask_post(payload: AskRequest):
    try:
        return await run_agent(payload.query.strip())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
