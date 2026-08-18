"""Validation and normalization for structured LLM decisions."""

from dataclasses import dataclass
from typing import Any


class LLMDecisionError(ValueError):
    """Raised when an LLM response is not a valid JARVIS decision."""


@dataclass(frozen=True)
class LLMDecision:
    """A validated action selected by the LLM."""

    tool: str
    arguments: dict[str, Any]
    response: str


def parse_decision(payload: dict[str, Any]) -> LLMDecision:
    """Validate a decoded JSON decision from the LLM."""
    if not isinstance(payload, dict):
        raise LLMDecisionError("LLM decision must be an object.")

    tool = payload.get("tool")
    arguments = payload.get("arguments", {})
    response = payload.get("response", "")

    if not isinstance(tool, str) or not tool.strip():
        raise LLMDecisionError("LLM decision is missing a tool name.")

    if not isinstance(arguments, dict):
        raise LLMDecisionError("LLM decision arguments must be an object.")

    if not isinstance(response, str):
        raise LLMDecisionError("LLM decision response must be a string.")

    return LLMDecision(
        tool=tool.strip(),
        arguments=arguments,
        response=response.strip(),
    )
