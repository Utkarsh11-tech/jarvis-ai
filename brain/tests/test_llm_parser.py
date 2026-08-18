"""Tests for structured local-LLM decisions."""

import pytest

from brain.llm.parser import LLMDecisionError, parse_decision


def test_parse_valid_decision():
    decision = parse_decision(
        {
            "tool": "open_application",
            "arguments": {"target": "chrome"},
            "response": "Opening Chrome.",
        }
    )

    assert decision.tool == "open_application"
    assert decision.arguments == {"target": "chrome"}
    assert decision.response == "Opening Chrome."


def test_parse_rejects_missing_tool():
    with pytest.raises(LLMDecisionError):
        parse_decision({"arguments": {}, "response": ""})


def test_parse_rejects_non_object_arguments():
    with pytest.raises(LLMDecisionError):
        parse_decision(
            {
                "tool": "open_application",
                "arguments": "chrome",
                "response": "Opening Chrome.",
            }
        )
