"""
Session logger for FounderOS.
Uses /tmp/sessions.db on Vercel (ephemeral but functional within a lambda invocation).
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, List

# /tmp is the only writable directory on Vercel serverless functions
DB_PATH = "/tmp/founderos_sessions.db"


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            idea TEXT,
            industry TEXT,
            brief_json TEXT,
            eval_json TEXT,
            elapsed_seconds REAL,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


_init_db()


def log_session(
    session_id: str,
    idea: str,
    industry: str,
    brief: Dict[str, Any],
    eval_scores: Dict[str, Any],
    elapsed: float,
) -> None:
    try:
        conn = _get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO sessions VALUES (?,?,?,?,?,?,?)",
            (
                session_id,
                idea,
                industry,
                json.dumps(brief),
                json.dumps(eval_scores),
                elapsed,
                datetime.now().isoformat(),
            ),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass  # Non-fatal on Vercel


def get_all_sessions() -> List[Dict[str, Any]]:
    try:
        conn = _get_conn()
        rows = conn.execute(
            "SELECT id, idea, industry, eval_json, elapsed_seconds, created_at FROM sessions ORDER BY created_at DESC LIMIT 50"
        ).fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append({
                "id": row["id"],
                "idea": row["idea"],
                "industry": row["industry"],
                "eval": json.loads(row["eval_json"]),
                "elapsed_seconds": row["elapsed_seconds"],
                "created_at": row["created_at"],
            })
        return result
    except Exception:
        return []
