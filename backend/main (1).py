from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
import json
import uuid
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

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

# Serve frontend static files
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


class IdeaInput(BaseModel):
    idea: str
    industry: str = "general"


@app.get("/")
async def root():
    index = os.path.join(os.path.dirname(__file__), "frontend", "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {"status": "FounderOS API running", "version": "1.0.0", "ui": "/app"}


@app.get("/app")
async def serve_app():
    index = os.path.join(os.path.dirname(__file__), "frontend", "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {"error": "Frontend not found. Make sure frontend/index.html exists in the container."}


@app.post("/api/launch")
async def launch_agents(input_data: IdeaInput):
    """Stream agent activity as Server-Sent Events"""
    session_id = str(uuid.uuid4())

    async def event_stream():
        try:
            yield f"data: {json.dumps({'type': 'session_start', 'session_id': session_id, 'timestamp': datetime.now().isoformat()})}\n\n"
            async for event in run_orchestrator(input_data.idea, input_data.industry, session_id):
                yield f"data: {json.dumps(event)}\n\n"
                await asyncio.sleep(0.05)
            yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/sessions")
async def get_sessions():
    return get_all_sessions()


@app.get("/api/health")
async def health():
    frontend_exists = os.path.exists(os.path.join(os.path.dirname(__file__), "frontend", "index.html"))
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "frontend_present": frontend_exists,
    }
