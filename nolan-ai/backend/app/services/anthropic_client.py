"""Thin wrapper around the Anthropic SDK shared by all three agents.

Centralizes model selection, the Claude web search tool (used by the
Search Engine Agent's research tasks and the Script Agent's fact-check
task), and basic retry-free error surfacing — callers decide what
"critical" vs "log and continue" means for their own task.

Every call is logged with token usage and a breakdown of any tool Claude
actually invoked (not hardcoded to web search — this covers whatever
server-side tool shows up in the response, so adding a new tool later
doesn't require touching the logging). Visible in Render's Logs tab.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

import anthropic

from app.config import settings

logger = logging.getLogger(__name__)

_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

# max_uses hard-caps how many searches Claude can run in a single request —
# without it, a prompt that merely suggests "search thoroughly" has no limit,
# and every search's results (page snippets, sometimes full pages) get added
# to that same request's input tokens. A handful of targeted searches is
# plenty for topic discovery; there's no reason for this to be unbounded.
DEFAULT_MAX_WEB_SEARCHES = 5


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
    max_web_searches: int = DEFAULT_MAX_WEB_SEARCHES,
    temperature: float = 1.0,
    context: str = "",
) -> ClaudeResponse:
    """Single non-streaming call to Claude. Raises anthropic.APIError on failure —
    callers are responsible for catching it and routing to their error handling tier.

    `context` is a free-text label (e.g. "search_agent.search_subarea") used
    only for the usage log line below — it identifies which agent/step made
    the call, since this wrapper is shared by all three agents."""
    tools = (
        [{"type": "web_search_20250305", "name": "web_search", "max_uses": max_web_searches}]
        if use_web_search
        else None
    )

    response = _client.messages.create(
        model=settings.anthropic_model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=messages,
        tools=tools,
    )

    _log_usage(context, response)

    text_blocks = [block.text for block in response.content if block.type == "text"]
    return ClaudeResponse(
        text="\n".join(text_blocks),
        stop_reason=response.stop_reason,
        raw=response,
    )


def _log_usage(context: str, response) -> None:
    """Logs token usage plus a breakdown of any tool Claude invoked — the
    tool's name and how it was called (tool_calls), and how many results
    came back per call (tool_results). Deliberately doesn't log result
    *content* (e.g. page snippets) — only counts, to keep this cheap to
    store and free of anything we'd need to worry about retaining."""
    tool_calls = []
    tool_results = []

    for block in getattr(response, "content", []):
        block_type = getattr(block, "type", "")
        if block_type == "server_tool_use":
            tool_calls.append({"tool": block.name, "input": block.input})
        elif block_type.endswith("_tool_result"):
            tool_name = block_type.removesuffix("_tool_result")
            content = getattr(block, "content", None)
            if isinstance(content, list):
                tool_results.append({"tool": tool_name, "result_count": len(content)})
            else:
                tool_results.append({"tool": tool_name, "result_count": 0, "error": True})

    usage = response.usage
    logger.info(
        "claude_api_call context=%s model=%s input_tokens=%d output_tokens=%d "
        "tool_calls=%s tool_results=%s",
        context or "unlabeled",
        response.model,
        usage.input_tokens,
        usage.output_tokens,
        tool_calls,
        tool_results,
    )
