from typing import AsyncGenerator
import json
import re
from agents.base_agent import BaseAgent

SYSTEM_PROMPT = """You are a world-class startup market strategist. Analyze startup ideas with precision and deliver actionable, data-grounded insights. Output structured JSON only. Be specific with numbers — estimate TAM/SAM/SOM using bottoms-up logic. Name real competitors. Be honest about risks."""


class StrategistAgent(BaseAgent):
    def __init__(self):
        super().__init__("Strategist", "Market Research & Competitive Analysis")

    async def run(self, context: dict) -> AsyncGenerator[dict, None]:
        idea = context.get("idea", "")
        industry = context.get("industry", "general")

        yield {"type": "agent_status", "agent": self.name, "status": "thinking",
               "message": "Analyzing market landscape and sizing opportunity..."}

        prompt = f"""Analyze this startup idea from a market strategy perspective.

IDEA: {idea}
INDUSTRY: {industry}

Return ONLY a JSON object with this exact structure (no markdown, no explanation):
{{
  "market_summary": "2-3 sentence executive summary of the market opportunity",
  "tam": {{"value": "$47B", "logic": "bottoms-up reasoning"}},
  "sam": {{"value": "$8B", "logic": "serviceable addressable market reasoning"}},
  "som": {{"value": "$400M", "logic": "realistically capturable in 3-5 years"}},
  "competitors": [
    {{"name": "Company", "strength": "Their key advantage", "weakness": "Their key gap", "positioning": "How they position"}}
  ],
  "market_gaps": ["Gap 1", "Gap 2", "Gap 3"],
  "market_trends": ["Trend 1", "Trend 2", "Trend 3"],
  "risks": ["Risk 1", "Risk 2"],
  "score": 7
}}

Include 3-4 real competitors. Return ONLY the JSON."""

        raw = await self.think(prompt, SYSTEM_PROMPT, max_tokens=1500)

        try:
            clean = re.sub(r"```json\n?|```\n?", "", raw).strip()
            # find first { to last }
            start = clean.find("{")
            end = clean.rfind("}") + 1
            if start != -1 and end > start:
                clean = clean[start:end]
            data = json.loads(clean)
        except Exception:
            data = {
                "market_summary": raw[:300] if raw else "Parse failed.",
                "tam": {"value": "N/A", "logic": ""}, "sam": {"value": "N/A", "logic": ""},
                "som": {"value": "N/A", "logic": ""}, "competitors": [],
                "market_gaps": [], "market_trends": [], "risks": [], "score": 5,
                "error": "parse_failed",
            }

        yield {"type": "agent_status", "agent": self.name, "status": "done",
               "message": f"Market analysis complete. {len(data.get('competitors', []))} competitors identified."}
        yield {"type": "agent_result", "agent": self.name, "data": data}
