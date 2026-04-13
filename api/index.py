from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
except Exception:
    pass

from orchestrator.graph import run_orchestrator_sync
from eval.logger import get_all_sessions

app = FastAPI(title="FounderOS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IdeaInput(BaseModel):
    idea: str
    industry: str = "general"


@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "env_key_set": bool(os.getenv("GEMINI_API_KEY")),
    }


@app.get("/api/sessions")
async def get_sessions():
    return get_all_sessions()


@app.post("/api/launch")
async def launch_agents(input_data: IdeaInput):
    """
    Runs all agents and returns a single JSON response.
    Vercel/Lambda buffers responses so SSE streaming is replaced
    with a regular JSON endpoint. The frontend handles this accordingly.
    """
    session_id = str(uuid.uuid4())
    try:
        result = await run_orchestrator_sync(
    input_data.idea,
    input_data.industry,
    session_id
)

print("🚀 ORCHESTRATOR RESULT:", result)

# 🔥 SAFETY FIX
if not result or not isinstance(result, dict):
    return JSONResponse(content={
        "events": [],
        "data": {},
        "eval": {},
        "session_id": session_id,
        "type": "error",
        "message": "Empty orchestrator result"
    })

    # Ensure required fields exist
    result.setdefault("events", [])
    result.setdefault("data", {})
    result.setdefault("eval", {})
    result.setdefault("session_id", session_id)
    
    return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"type": "error", "message": str(e), "session_id": session_id}
        )
