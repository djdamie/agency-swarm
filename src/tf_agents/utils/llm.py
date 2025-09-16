"""LLM client helpers for TF agents."""

from __future__ import annotations

import os
from typing import Iterable

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

__all__ = [
    "get_async_openai_client",
    "get_model_name",
    "call_json_llm",
]


_client: AsyncOpenAI | None = None


def get_async_openai_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("LLM_BASE_URL")
        if api_key is None and base_url is None:
            raise RuntimeError("No GROQ_API_KEY/OPENAI_API_KEY or LLM_BASE_URL configured")
        _client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    return _client


def get_model_name(default: str = "openai/gpt-oss-20b") -> str:
    return os.environ.get("LLM_MODEL", default)


async def call_json_llm(system_prompt: str, user_content: str) -> str:
    """Run a chat completion and return the assistant content."""
    client = get_async_openai_client()
    model = get_model_name()
    chat = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    )
    return chat.choices[0].message.content or ""
