"""Local Ollama client for the JARVIS reasoning layer."""

from __future__ import annotations

import json
import os
from typing import Any

import requests
from dotenv import load_dotenv

from brain.llm.parser import LLMDecision, LLMDecisionError, parse_decision
from brain.llm.prompt import (
    SYSTEM_PROMPT,
    build_decision_schema,
    build_user_input,
)
from brain.tools.registry import ToolRegistry, get_default_registry


class LLMError(RuntimeError):
    """Raised when the local LLM cannot produce a valid JARVIS decision."""


class LLMClient:
    """Provider-independent client for a local Ollama model."""

    def __init__(
        self,
        model: str | None = None,
        host: str | None = None,
        timeout: float = 120.0,
        registry: ToolRegistry | None = None,
    ) -> None:
        load_dotenv()

        self.model = model or os.getenv("JARVIS_LLM_MODEL", "qwen3:8b")
        self.host = (host or os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")).rstrip("/")
        self.timeout = timeout
        self.registry = registry or get_default_registry()

    def decide(self, command: str, context: str = "") -> LLMDecision:
        """Turn a natural-language request into one validated tool decision."""
        command = command.strip()
        if not command:
            raise LLMError("Cannot ask the LLM to plan an empty command.")

        tools = self.registry.describe()
        payload = {
            "model": self.model,
            "stream": False,
            "think": False,
            "format": build_decision_schema(tools),
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_user_input(command, context, tools),
                },
            ],
        }

        try:
            response = requests.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as error:
            raise LLMError(
                "Could not reach Ollama. Make sure Ollama is running and the "
                f"'{self.model}' model is installed."
            ) from error
        except ValueError as error:
            raise LLMError("Ollama returned invalid JSON.") from error

        content = ((data.get("message") or {}).get("content") or "").strip()
        if not content:
            raise LLMError("Ollama returned an empty model response.")

        try:
            decision_payload: dict[str, Any] = json.loads(content)
            decision = parse_decision(decision_payload)
        except (json.JSONDecodeError, LLMDecisionError) as error:
            raise LLMError(f"Invalid JARVIS decision from Ollama: {error}") from error

        if decision.tool != "unknown_request" and self.registry.get(decision.tool) is None:
            raise LLMError(f"LLM selected an unavailable tool: {decision.tool}")

        return decision
