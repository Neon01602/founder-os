from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
import uuid
import os
import sys
from datetime import datetime

# Add api/ dir to sys.path so relative imports work on Vercel
sys.path.insert(0, os.path.dirname(__file__))

# Load env vars for local dev (Vercel injects them automatically)
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
except Exception:
    pass

from orchestrator.graph import run_orchestrator
from eval.logger import log_session, get_all_sessions

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
        "env_key_set": bool(os.getenv("OPENROUTER_API_KEY")),
    }


@app.get("/api/sessions")
async def get_sessions():
    return get_all_sessions()


@app.post("/api/launch")
async def launch_agents(input_data: IdeaInput):
    """Stream agent activity as Server-Sent Events.
    
    NOTE: Mangum is intentionally NOT used here — it buffers the full
    response before returning, which breaks SSE streaming. Vercel's
    Python runtime supports ASGI streaming natively via the `app` export.
    """
    session_id = str(uuid.uuid4())

    async def event_stream():
        try:
            yield f"data: {json.dumps({'type': 'session_start', 'session_id': session_id, 'timestamp': datetime.now().isoformat()})}\n\n"
            async for event in run_orchestrator(input_data.idea, input_data.industry, session_id):
                yield f"data: {json.dumps(event)}\n\n"
                await asyncio.sleep(0.01)
            yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# Vercel detects this `app` export automatically as an ASGI app.
# Do NOT wrap with Mangum — it breaks streaming.
