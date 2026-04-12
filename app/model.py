from __future__ import annotations

from openai import OpenAI

from app.settings import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL


client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url=GROQ_BASE_URL,
)


def get_model_name() -> str:
    return GROQ_MODEL


def create_response(messages: list[dict], tools: list[dict] | None = None):
    """
    Groq의 OpenAI-compatible chat completion 호출
    """
    kwargs = {
        "model": GROQ_MODEL,
        "messages": messages,
    }

    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    return client.chat.completions.create(**kwargs)