from typing import AsyncGenerator
import json
import re
from agents.base_agent import BaseAgent

SYSTEM_PROMPT = """You are a world-class product manager. Write crisp, opinionated PRDs. Prioritize ruthlessly using ICE scoring (Impact x Confidence x Ease). Output structured JSON only."""


class ProductAgent(BaseAgent):
    def __init__(self):
        super().__init__("Product", "PRD & Feature Strategy")

    async def run(self, context: dict) -> AsyncGenerator[dict, None]:
        idea = context.get("idea", "")
        market_data = context.get("strategist_result", {})
        research_data = context.get("user_research_result", {})

        yield {"type": "agent_status", "agent": self.name, "status": "thinking",
               "message": "Writing PRD and prioritizing feature roadmap..."}

        personas = research_data.get("personas", [])
        persona_names = [p.get("name", "") for p in personas[:3]]
        pain_points = research_data.get("common_pain_points", [])[:4]
        jobs = research_data.get("jobs_to_be_done", [])[:2]
        market_gaps = market_data.get("market_gaps", [])[:3]

        prompt = f"""Create a Product Requirements Document for this startup.

STARTUP IDEA: {idea}
TARGET PERSONAS: {', '.join(persona_names) or 'General users'}
KEY PAIN POINTS: {json.dumps(pain_points)}
MARKET GAPS: {json.dumps(market_gaps)}

Return ONLY a JSON object with this exact structure (no markdown):
{{
  "product_name": "Catchy product name",
  "tagline": "One-line value proposition",
  "problem_statement": "Clear 2-sentence problem definition",
  "solution_statement": "Clear 2-sentence solution definition",
  "core_features": [
    {{
      "id": "F1",
      "name": "Feature name",
      "description": "What it does and why it matters",
      "user_story": "As a [persona], I want [action] so that [outcome]",
      "impact": 9,
      "confidence": 8,
      "ease": 6,
      "ice_score": 432,
      "phase": "MVP",
      "acceptance_criteria": ["Criterion 1", "Criterion 2"]
    }}
  ],
  "mvp_scope": {{
    "included": ["Feature 1", "Feature 2", "Feature 3"],
    "excluded": ["What is NOT in MVP"],
    "success_metrics": ["Metric 1", "Metric 2"]
  }},
  "wireframe_descriptions": [
    {{
      "screen": "Screen name",
      "description": "What this screen does",
      "key_elements": ["Element 1", "Element 2"]
    }}
  ],
  "go_to_market": {{
    "primary_channel": "Main acquisition channel",
    "secondary_channels": ["Channel 2", "Channel 3"],
    "launch_strategy": "Specific launch approach",
    "pricing_model": "Pricing strategy with tiers",
    "first_100_users": "Specific plan to get first 100 users"
  }},
  "technical_stack": {{
    "frontend": "Recommended frontend tech",
    "backend": "Recommended backend tech",
    "infrastructure": "Cloud/infra recommendation",
    "key_integrations": ["Integration 1", "Integration 2"]
  }},
  "milestones": [
    {{"week": "Week 1-2", "goal": "Milestone description"}},
    {{"week": "Week 3-4", "goal": "Milestone description"}},
    {{"week": "Week 5-8", "goal": "Milestone description"}},
    {{"week": "Week 9-12", "goal": "Milestone description"}}
  ]
}}

Include 5-7 core features sorted by ICE score descending. Return ONLY the JSON."""

        raw = await self.think(prompt, SYSTEM_PROMPT, max_tokens=2500)

        try:
            clean = re.sub(r"```json\n?|```\n?", "", raw).strip()
            start = clean.find("{")
            end = clean.rfind("}") + 1
            if start != -1 and end > start:
                clean = clean[start:end]
            data = json.loads(clean)
        except Exception:
            data = {
                "product_name": "Your Product", "tagline": "Tagline unavailable",
                "problem_statement": "Could not parse product data.",
                "solution_statement": "", "core_features": [],
                "mvp_scope": {"included": [], "excluded": [], "success_metrics": []},
                "wireframe_descriptions": [],
                "go_to_market": {"primary_channel": "", "pricing_model": "",
                                 "first_100_users": "", "launch_strategy": "", "secondary_channels": []},
                "technical_stack": {"frontend": "", "backend": "", "infrastructure": "", "key_integrations": []},
                "milestones": [], "error": "parse_failed",
            }

        yield {"type": "agent_status", "agent": self.name, "status": "done",
               "message": f"PRD complete. {len(data.get('core_features', []))} features prioritized."}
        yield {"type": "agent_result", "agent": self.name, "data": data}
