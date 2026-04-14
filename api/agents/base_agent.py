import re
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncGenerator
from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))


class BaseAgent(ABC):
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def extract_json(self, raw: str) -> str:
        # Strip markdown code fences — re was previously missing, causing NameError
        clean = re.sub(r"```json\n?|```\n?", "", raw).strip()
        start = clean.find("{")
        end = clean.rfind("}") + 1
        if start != -1 and end > start:
            return clean[start:end]
        return clean

    def _call_groq_sync(self, prompt: str, system: str, max_tokens: int) -> str:
        """Blocking Groq call — run via asyncio.to_thread only."""
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content

    async def think(self, prompt: str, system: str, max_tokens: int = 2000) -> str:
        """Call Groq API without blocking the async event loop."""
        return await asyncio.to_thread(self._call_groq_sync, prompt, system, max_tokens)

    @abstractmethod
    async def run(self, context: dict) -> AsyncGenerator[dict, None]:
        pass
