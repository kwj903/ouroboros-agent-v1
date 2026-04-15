from __future__ import annotations

from openai import OpenAI

from app.settings import ALL_API_KEY, ALL_BASE_URL, ALL_MODEL


client = OpenAI(
    api_key=ALL_API_KEY,
    base_url=ALL_BASE_URL,
)


def get_model_name() -> str:
    return ALL_MODEL


def create_response(messages: list[dict], tools: list[dict] | None = None):
    """
    ALL의 OpenAI-compatible chat completion 호출
    """
    kwargs = {
        "model": ALL_MODEL,
        "messages": messages,
    }

    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    return client.chat.completions.create(**kwargs)