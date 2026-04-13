from abc import ABC, abstractmethod
from typing import AsyncGenerator
from openai import OpenAI
import os

client = OpenAI(
    base_url="deepseek/deepseek-chat:free",
    api_key=os.getenv("OPENROUTER_API_KEY", ""),
)


class BaseAgent(ABC):
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    async def think(self, prompt: str, system: str, max_tokens: int = 2000) -> str:
        """Call OpenRouter (DeepSeek V3) and return full response text."""
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324:free",
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