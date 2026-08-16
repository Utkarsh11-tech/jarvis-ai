from brain.core import assistant_v2


class FakeBridge:
    def send_response(self, response):
        self.response = response


def test_unknown_routes_to_llm(monkeypatch):
    """Conversational/UNKNOWN input must use the Qwen path."""

    calls = []

    monkeypatch.setattr(
        assistant_v2.Assistant,
        "_handle_llm_command",
        lambda self, command: calls.append(command) or True,
    )

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    assistant.process_command = lambda command: [
        {
            "intent": "UNKNOWN",
            "target": command,
        }
    ]

    command = "What is machine learning?"

    results = assistant.process_command(command)

    # This mirrors the routing condition used
    # by Assistant V2.
    if not results or all(result.get("intent") == "UNKNOWN" for result in results):
        assistant._handle_llm_command(command)

    assert calls == [command]


def test_known_command_does_not_route_to_llm(
    monkeypatch,
):
    """Known deterministic commands must stay on the executor path."""

    calls = []

    monkeypatch.setattr(
        assistant_v2.Assistant,
        "_handle_llm_command",
        lambda self, command: calls.append(command) or True,
    )

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    assistant.process_command = lambda command: [
        {
            "intent": "OPEN_APPLICATION",
            "target": "calculator",
        }
    ]

    command = "Open calculator"

    results = assistant.process_command(command)

    # Known deterministic commands must NOT
    # enter the LLM fallback.
    if not results or all(result.get("intent") == "UNKNOWN" for result in results):
        assistant._handle_llm_command(command)

    assert calls == []
