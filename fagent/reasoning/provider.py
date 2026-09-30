import os
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import httpx


DEFAULT_OPENROUTER_MODEL = "qwen/qwen-2.5-coder-32b-instruct:free"
OPENROUTER_FALLBACK_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemini-2.0-flash-exp:free",
    "deepseek/deepseek-chat:free",
]


class LLMProvider(ABC):
    """Abstract base class for provider-agnostic LLM reasoning."""

    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
        """Sends messages to the model and returns the response string."""
        pass


class OpenRouterProvider(LLMProvider):
    """OpenRouter provider implementation supporting free and fast coding models."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        self.model = model or os.environ.get("FAGENT_MODEL") or DEFAULT_OPENROUTER_MODEL
        self.timeout = timeout
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is not set. Please set the OPENROUTER_API_KEY environment variable "
                "or configure it in .fagent/config.json."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/kashifasiddiqui/Agent-Shin",
            "X-Title": "FAgent - Agentic Frontend Engineer",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2048,
        }

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                raise RuntimeError(f"OpenRouter returned empty choices: {data}")
            return choices[0].get("message", {}).get("content", "").strip()
