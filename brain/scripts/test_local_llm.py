"""Manual smoke test for the local Ollama-backed JARVIS LLM."""

from __future__ import annotations

import sys

from brain.llm import LLMClient


def main() -> int:
    command = " ".join(sys.argv[1:]).strip()

    if not command:
        command = input("JARVIS test command: ").strip()

    client = LLMClient()

    try:
        decision = client.decide(command)
    except Exception as error:
        print(f"LLM test failed: {error}")
        return 1

    print("Tool:", decision.tool)
    print("Arguments:", decision.arguments)
    print("Response:", decision.response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
