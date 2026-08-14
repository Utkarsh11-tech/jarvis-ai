import os

import requests


class OllamaClient:
    """
    Lightweight client for communicating with a local
    or remote Ollama server.

    Supports:
    - single-prompt generation
    - multi-turn conversation history
    - configurable Ollama server
    - configurable model
    """

    DEFAULT_BASE_URL = "http://localhost:11434"
    DEFAULT_MODEL = "qwen3:8b"
    DEFAULT_TIMEOUT = 300

    def __init__(
        self,
        base_url=None,
        model=None,
        timeout=None,
    ):
        self.base_url = (
            base_url
            or os.getenv(
                "OLLAMA_BASE_URL",
                self.DEFAULT_BASE_URL,
            )
        ).rstrip("/")

        self.model = model or os.getenv(
            "OLLAMA_MODEL",
            self.DEFAULT_MODEL,
        )

        self.timeout = (
            timeout
            if timeout is not None
            else int(
                os.getenv(
                    "OLLAMA_TIMEOUT",
                    self.DEFAULT_TIMEOUT,
                )
            )
        )

    # ==================================================
    # CONNECTION
    # ==================================================

    def is_available(self):
        """
        Checks whether the Ollama server is reachable.
        """

        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )

            return response.ok

        except requests.RequestException:
            return False

    # ==================================================
    # MODEL CHECK
    # ==================================================

    def has_model(self):
        """
        Checks whether the configured model exists
        on the Ollama server.
        """

        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )

            response.raise_for_status()

            data = response.json()

            models = data.get(
                "models",
                [],
            )

            for model in models:

                if model.get("name") == self.model:
                    return True

            return False

        except (
            requests.RequestException,
            ValueError,
        ):
            return False

    # ==================================================
    # GENERATE
    # ==================================================

    def generate(
        self,
        prompt,
        system_prompt=None,
        history=None,
    ):
        """
        Sends a prompt to Ollama and returns the
        generated response.

        Args:
            prompt:
                Current user prompt.

            system_prompt:
                Optional system instruction.

            history:
                Optional list of previous conversation
                messages.

                Example:

                [
                    {
                        "role": "user",
                        "content": "My name is Utkarsh.",
                    },
                    {
                        "role": "assistant",
                        "content": "Nice to meet you.",
                    },
                ]

        Returns:
            str: Generated model response.

        Raises:
            RuntimeError: If Ollama or the model is
            unavailable.
        """

        if not prompt:
            return ""

        if not self.is_available():

            raise RuntimeError("Ollama server is not available.")

        if not self.has_model():

            raise RuntimeError(f"Ollama model '{self.model}' " "is not available.")

        messages = []

        # --------------------------------------------------
        # SYSTEM PROMPT
        # --------------------------------------------------

        if system_prompt:

            messages.append(
                {
                    "role": "system",
                    "content": str(system_prompt).strip(),
                }
            )

        # --------------------------------------------------
        # CONVERSATION HISTORY
        # --------------------------------------------------

        if history:

            for message in history:

                if not isinstance(
                    message,
                    dict,
                ):
                    continue

                role = message.get("role")

                content = message.get("content")

                if role not in {
                    "system",
                    "user",
                    "assistant",
                }:
                    continue

                if not content:
                    continue

                messages.append(
                    {
                        "role": role,
                        "content": str(content).strip(),
                    }
                )

        # --------------------------------------------------
        # CURRENT USER MESSAGE
        # --------------------------------------------------

        messages.append(
            {
                "role": "user",
                "content": str(prompt).strip(),
            }
        )

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }

        try:

            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()

            data = response.json()

        except requests.RequestException as error:

            raise RuntimeError(f"Ollama request failed: {error}") from error

        except ValueError as error:

            raise RuntimeError("Ollama returned invalid JSON.") from error

        message = data.get(
            "message",
            {},
        )

        if not isinstance(
            message,
            dict,
        ):

            raise RuntimeError("Ollama returned an invalid " "message structure.")

        result = message.get(
            "content",
            "",
        )

        if not isinstance(
            result,
            str,
        ):

            raise RuntimeError("Ollama returned an invalid " "response.")

        return result.strip()

    # ==================================================
    # MODEL INFO
    # ==================================================

    def get_model(self):
        """
        Returns the configured model name.
        """

        return self.model

    def get_base_url(self):
        """
        Returns the configured Ollama URL.
        """

        return self.base_url

    def get_timeout(self):
        """
        Returns the configured request timeout.
        """

        return self.timeout
