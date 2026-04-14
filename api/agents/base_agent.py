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
        clean = re.sub(r"```json\n?|```\n?", "", raw).strip()
        start = clean.find("{")
        end = clean.rfind("}") + 1
        if start != -1 and end > start:
            return clean[start:end]
        return clean

    async def think(self, prompt: str, system: str, max_tokens: int = 2000) -> str:
        """Call Groq API and return full response text."""
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content

    @abstractmethod
    async def run(self, context: dict) -> AsyncGenerator[dict, None]:
        pass
