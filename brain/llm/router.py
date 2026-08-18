"""Remote-first/local-fallback routing for the JARVIS Ollama brain."""

from __future__ import annotations

import os
from typing import Callable

from dotenv import load_dotenv

from brain.llm.client import LLMClient, LLMDecision, LLMError


class LLMRouterError(RuntimeError):
    """Raised when the configured LLM route cannot produce a decision."""


class LLMRouter:
    """Route JARVIS LLM requests between remote and local Ollama servers.

    Modes:
        AUTO: remote first, then local fallback.
        REMOTE: remote only, never falls back.
        LOCAL: local only.
    """

    VALID_MODES = {"AUTO", "REMOTE", "LOCAL"}

    def __init__(
        self,
        remote_client: LLMClient | None = None,
        local_client: LLMClient | None = None,
        mode: str | None = None,
        remote_host: str | None = None,
        local_host: str | None = None,
        remote_model: str | None = None,
        local_model: str | None = None,
        timeout: float | None = None,
    ) -> None:
        load_dotenv()

        configured_mode = (mode or os.getenv("JARVIS_LLM_MODE", "AUTO")).strip().upper()
        if configured_mode not in self.VALID_MODES:
            raise ValueError(
                f"Invalid JARVIS_LLM_MODE '{configured_mode}'. "
                f"Expected one of {sorted(self.VALID_MODES)}."
            )

        default_timeout = float(os.getenv("JARVIS_LLM_TIMEOUT", "30"))
        timeout = default_timeout if timeout is None else timeout

        self.mode = configured_mode
        self.remote_client = remote_client or LLMClient(
            model=remote_model or os.getenv("JARVIS_LLM_REMOTE_MODEL", "qwen3:8b"),
            host=remote_host or os.getenv(
                "JARVIS_LLM_REMOTE_HOST",
                "http://127.0.0.1:11434",
            ),
            timeout=timeout,
        )
        self.local_client = local_client or LLMClient(
            model=local_model or os.getenv("JARVIS_LLM_LOCAL_MODEL", "qwen3:8b"),
            host=local_host or os.getenv(
                "JARVIS_LLM_LOCAL_HOST",
                "http://127.0.0.1:11434",
            ),
            timeout=timeout,
        )

    def decide(self, command: str, context: str = "") -> LLMDecision:
        """Return the first successful decision according to the active mode."""
        if self.mode == "LOCAL":
            return self._call(self.local_client, command, context)

        if self.mode == "REMOTE":
            return self._call(self.remote_client, command, context)

        # AUTO deliberately prefers the dedicated LLM machine.
        try:
            return self._call(self.remote_client, command, context)
        except LLMError as remote_error:
            try:
                return self._call(self.local_client, command, context)
            except LLMError as local_error:
                raise LLMRouterError(
                    "Both remote and local Ollama LLMs failed. "
                    f"Remote: {remote_error}; Local: {local_error}"
                ) from local_error

    @staticmethod
    def _call(
        client: LLMClient,
        command: str,
        context: str,
    ) -> LLMDecision:
        return client.decide(command, context)


def get_default_router() -> LLMRouter:
    """Build a router from the current JARVIS environment."""
    return LLMRouter()
