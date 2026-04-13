from abc import ABC, abstractmethod
from typing import AsyncGenerator
import google.generativeai as genai
import os

class BaseAgent(ABC):
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    async def think(self, prompt: str, system: str, max_tokens: int = 2000) -> str:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=system
        )
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(max_output_tokens=max_tokens)
        )
        return response.text

    @abstractmethod
    async def run(self, context: dict) -> AsyncGenerator[dict, None]:
        pass
