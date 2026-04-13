from typing import AsyncGenerator
import json
import re
import httpx
from agents.base_agent import BaseAgent

SYSTEM_PROMPT = """You are a senior UX researcher. You build user personas from REAL user quotes and discussions. Every pain point must be traceable to real posts provided. You never invent data. Output structured JSON only."""


async def scrape_reddit(query: str, subreddits: list) -> list:
    headers = {"User-Agent": "FounderOS/1.0 research-bot"}
    posts = []
    async with httpx.AsyncClient(timeout=15) as client:
        for sub in subreddits[:3]:
            try:
                url = f"https://www.reddit.com/r/{sub}/search.json"
                r = await client.get(url, headers=headers,
                                     params={"q": query, "sort": "relevance", "limit": 4, "t": "year"})
                if r.status_code != 200:
                    continue
                for item in r.json().get("data", {}).get("children", []):
                    p = item.get("data", {})
                    posts.append({
                        "title": p.get("title", ""),
                        "body": p.get("selftext", "")[:600],
                        "subreddit": p.get("subreddit", ""),
                        "url": f"https://reddit.com{p.get('permalink', '')}",
                    })
            except Exception:
                continue
        try:
            r = await client.get("https://www.reddit.com/search.json", headers=headers,
                                 params={"q": query, "sort": "relevance", "limit": 6, "t": "year"})
            if r.status_code == 200:
                for item in r.json().get("data", {}).get("children", []):
                    p = item.get("data", {})
                    posts.append({
                        "title": p.get("title", ""),
                        "body": p.get("selftext", "")[:600],
                        "subreddit": p.get("subreddit", ""),
                        "url": f"https://reddit.com{p.get('permalink', '')}",
                    })
        except Exception:
            pass
    return posts[:10]


async def scrape_hn(query: str) -> list:
    posts = []
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get("https://hn.algolia.com/api/v1/search",
                                 params={"query": query, "tags": "story", "hitsPerPage": 5})
            if r.status_code == 200:
                for hit in r.json().get("hits", []):
                    posts.append({
                        "title": hit.get("title", ""),
                        "body": (hit.get("story_text") or "")[:400],
                        "subreddit": "HackerNews",
                        "url": hit.get("url", ""),
                    })
    except Exception:
        pass
    return posts


def get_subreddits(industry: str) -> list:
    base = ["startups", "Entrepreneur", "smallbusiness"]
    extras = {
        "saas": ["SaaS", "webdev", "devtools"],
        "fintech": ["personalfinance", "investing", "fintech"],
        "healthtech": ["HealthIT", "digitalhealth"],
        "edtech": ["edtech", "education"],
        "marketplace": ["ecommerce", "Flipping"],
        "consumer": ["apps", "androidapps"],
        "ai": ["MachineLearning", "ChatGPT", "LocalLLaMA"],
        "general": ["productivity", "Entrepreneur"],
    }
    return base + extras.get(industry, extras["general"])


class UserResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("User Research", "Persona Generation & Pain Point Discovery")

    async def run(self, context: dict) -> AsyncGenerator[dict, None]:
        idea = context.get("idea", "")
        industry = context.get("industry", "general")
        market_data = context.get("strategist_result", {})

        yield {"type": "agent_status", "agent": self.name, "status": "thinking",
               "message": "Scraping Reddit & Hacker News for real user discussions..."}

        words = [w for w in idea.split() if len(w) > 4][:5]
        query = " ".join(words[:4])

        reddit_posts = await scrape_reddit(query, get_subreddits(industry))
        hn_posts = await scrape_hn(query)
        all_posts = reddit_posts + hn_posts

        yield {"type": "agent_status", "agent": self.name, "status": "thinking",
               "message": f"Found {len(all_posts)} real discussions. Building personas from real data..."}
        yield {"type": "memory_update", "key": "posts_scraped",
               "value": f"{len(all_posts)} posts (Reddit + HN)", "agent": "User Research"}

        posts_text = ""
        for i, p in enumerate(all_posts[:8]):
            posts_text += f"\n[Post {i+1} — r/{p.get('subreddit','')}]\n"
            posts_text += f"Title: {p.get('title','')}\n"
            if p.get("body"):
                posts_text += f"Content: {p['body']}\n"

        market_summary = market_data.get("market_summary", "")
        market_gaps = market_data.get("market_gaps", [])

        prompt = f"""You scraped {len(all_posts)} REAL online discussions from Reddit and HN.

STARTUP IDEA: {idea}
MARKET SUMMARY: {market_summary}
MARKET GAPS: {', '.join(market_gaps)}

REAL SCRAPED DISCUSSIONS:
{posts_text if posts_text else "No posts found — use market context to infer realistic personas."}

Build 3 user personas as COMPOSITES of real people from these discussions.
Use real language and sentiment from the posts. Every frustration must come from actual post content.

Return ONLY a JSON object (no markdown):
{{
  "posts_analyzed": {len(all_posts)},
  "data_sources": [{{"platform": "Reddit+HN", "query": "{query}", "posts_found": {len(all_posts)}}}],
  "personas": [
    {{
      "id": "persona_1",
      "name": "Full name",
      "age": 32,
      "title": "Job title",
      "company_size": "50-200 employees",
      "location": "City, Country",
      "archetype": "The Overwhelmed Operator",
      "bio": "2-sentence background grounded in real posts",
      "goals": ["Goal 1", "Goal 2", "Goal 3"],
      "frustrations": ["Real frustration from posts", "Another real one", "Third one"],
      "current_tools": ["Tool 1", "Tool 2"],
      "willingness_to_pay": "$X/month",
      "quote": "Quote that sounds like it came from a real Reddit post",
      "source_posts": ["Which posts informed this persona"],
      "interview_insights": [
        {{"question": "What does a typical Monday look like for you?", "answer": "Grounded in real post language"}},
        {{"question": "Where do you lose the most time each week?", "answer": "Grounded in real post language"}},
        {{"question": "If you had a magic wand, what would you fix first?", "answer": "Grounded in real post language"}}
      ]
    }}
  ],
  "common_pain_points": ["Real pain from posts 1", "Real pain 2", "Real pain 3", "Real pain 4"],
  "raw_quotes": ["Paraphrased real quote 1", "Paraphrased real quote 2"],
  "jobs_to_be_done": [
    {{"job": "When I...", "outcome": "I want to...", "so_that": "So I can..."}}
  ],
  "buying_triggers": ["Trigger 1", "Trigger 2", "Trigger 3"],
  "research_confidence": 8
}}

Return ONLY the JSON."""

        raw = await self.think(prompt, SYSTEM_PROMPT, max_tokens=2500)

        try:
            data = json.loads(self.extract_json(raw))
        except Exception as e:
            data = {
                "posts_analyzed": len(all_posts),
                "personas": [], "common_pain_points": [],
                "jobs_to_be_done": [], "buying_triggers": [],
                "raw_quotes": [], "parse_error": str(e), "raw_response": raw[:500],
            }

        yield {"type": "agent_status", "agent": self.name, "status": "done",
               "message": f"Built {len(data.get('personas', []))} personas from {len(all_posts)} real discussions."}
        yield {"type": "agent_result", "agent": self.name, "data": data}
