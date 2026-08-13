"""Tests for the local Ollama LLM client."""

from brain.llm.client import LLMClient


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_client_converts_ollama_json_to_decision(monkeypatch):
    def fake_post(*args, **kwargs):
        assert args[0] == "http://127.0.0.1:11434/api/chat"
        assert kwargs["json"]["model"] == "qwen3:8b"
        assert kwargs["json"]["stream"] is False
        assert kwargs["json"]["think"] is False
        return FakeResponse(
            {
                "message": {
                    "content": (
                        '{"tool":"open_application",'
                        '"arguments":{"target":"chrome"},'
                        '"response":"Opening Chrome."}'
                    )
                }
            }
        )

    monkeypatch.setattr("brain.llm.client.requests.post", fake_post)

    client = LLMClient(model="qwen3:8b")
    decision = client.decide("Open Chrome.")

    assert decision.tool == "open_application"
    assert decision.arguments == {"target": "chrome"}
    assert decision.response == "Opening Chrome."
