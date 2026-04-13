"""
FounderOS Orchestrator — sync version for Vercel Lambda.
Collects all agent output and returns one dict instead of streaming.
"""
from typing import Dict, Any
from datetime import datetime
import time

from agents.strategist import StrategistAgent
from agents.user_research import UserResearchAgent
from agents.product import ProductAgent
from eval.scorer import score_session
from eval.logger import log_session


async def run_orchestrator_sync(idea: str, industry: str, session_id: str) -> Dict[str, Any]:
    start_time = time.time()
    context: dict = {"idea": idea, "industry": industry, "session_id": session_id}
    events = []

    def evt(type_, **kwargs):
        events.append({"type": type_, **kwargs})

    evt("session_start", session_id=session_id, timestamp=datetime.now().isoformat())
    evt("orchestrator", message=f"Analyzing idea in the {industry} space. Dispatching agents...")

    # ── 1. Strategist ────────────────────────────────────────────────
    strategist_result = {}
    try:
        strategist = StrategistAgent()
        async for event in strategist.run(context):
            if event["type"] == "agent_result":
                strategist_result = event.get("data", {})
            else:
                events.append(event)
    except Exception as e:
        evt("agent_status", agent="Strategist", status="done", message=f"Error: {str(e)[:120]}")
        strategist_result = {
            "market_summary": "Market analysis unavailable.",
            "tam": {"value": "N/A", "logic": ""}, "sam": {"value": "N/A", "logic": ""},
            "som": {"value": "N/A", "logic": ""}, "competitors": [],
            "market_gaps": [], "market_trends": [], "risks": [],
        }
    context["strategist_result"] = strategist_result
    evt("orchestrator", message="Strategist done. Dispatching User Research agent...")

    # ── 2. User Research ─────────────────────────────────────────────
    research_result = {}
    try:
        research_agent = UserResearchAgent()
        async for event in research_agent.run(context):
            if event["type"] == "agent_result":
                research_result = event.get("data", {})
            else:
                events.append(event)
    except Exception as e:
        evt("agent_status", agent="User Research", status="done", message=f"Error: {str(e)[:120]}")
        research_result = {"personas": [], "common_pain_points": [], "jobs_to_be_done": [], "buying_triggers": []}
    context["user_research_result"] = research_result
    evt("orchestrator", message="Research done. Dispatching Product agent...")

    # ── 3. Product ────────────────────────────────────────────────────
    product_result = {}
    try:
        product_agent = ProductAgent()
        async for event in product_agent.run(context):
            if event["type"] == "agent_result":
                product_result = event.get("data", {})
            else:
                events.append(event)
    except Exception as e:
        evt("agent_status", agent="Product", status="done", message=f"Error: {str(e)[:120]}")
        product_result = {
            "product_name": "Your Product", "tagline": "", "problem_statement": "",
            "solution_statement": "", "core_features": [],
            "mvp_scope": {"included": [], "excluded": [], "success_metrics": []},
            "go_to_market": {"primary_channel": "", "pricing_model": "", "first_100_users": "", "launch_strategy": ""},
            "technical_stack": {"frontend": "", "backend": ""}, "milestones": [],
        }
    context["product_result"] = product_result

    # ── 4. Assemble brief + eval ─────────────────────────────────────
    elapsed = round(time.time() - start_time, 1)
    brief = {
        "session_id": session_id, "idea": idea, "industry": industry,
        "generated_at": datetime.now().isoformat(), "elapsed_seconds": elapsed,
        "market": strategist_result, "research": research_result, "product": product_result,
    }

    try:
        eval_scores = score_session(brief)
    except Exception:
        eval_scores = {"overall": {"score": 0, "grade": "F"}}

    try:
        log_session(session_id=session_id, idea=idea, industry=industry,
                    brief=brief, eval_scores=eval_scores, elapsed=elapsed)
    except Exception:
        pass

    evt("orchestrator", message=f"All agents complete in {elapsed}s. Brief ready!")

    return {
        "type": "brief_ready",
        "session_id": session_id,
        "data": brief,
        "eval": eval_scores,
        "events": events,
    }
