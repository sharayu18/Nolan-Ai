"""Thin wrapper around the Anthropic SDK shared by all three agents.

Centralizes model selection, the Claude web search tool (used by the
Search Engine Agent's research tasks and the Script Agent's fact-check
task), and basic retry-free error surfacing — callers decide what
"critical" vs "log and continue" means for their own task.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import anthropic

from app.config import settings

_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

WEB_SEARCH_TOOL = {"type": "web_search_20250305", "name": "web_search"}


@dataclass
class ClaudeResponse:
    text: str
    stop_reason: str | None = None
    raw: object = field(default=None, repr=False)


def call_claude(
    system_prompt: str,
    messages: list[dict],
    *,
    max_tokens: int = 4096,
    use_web_search: bool = False,
    temperature: float = 1.0,
) -> ClaudeResponse:
    """Single non-streaming call to Claude. Raises anthropic.APIError on failure —
    callers are responsible for catching it and routing to their error handling tier."""
    tools = [WEB_SEARCH_TOOL] if use_web_search else None

    response = _client.messages.create(
        model=settings.anthropic_model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=messages,
        tools=tools,
    )

    text_blocks = [block.text for block in response.content if block.type == "text"]
    return ClaudeResponse(
        text="\n".join(text_blocks),
        stop_reason=response.stop_reason,
        raw=response,
    )
