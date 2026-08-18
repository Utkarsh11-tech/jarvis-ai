"""Prompt and structured-output schema for the local JARVIS LLM."""

SYSTEM_PROMPT = """You are the reasoning layer of JARVIS, a desktop AI assistant.

Your job is to understand the user's request and select exactly one available
JARVIS tool. Never invent a tool. Never invent arguments that are not supported
by the selected tool schema.

Return ONLY the JSON object requested by the output schema. Do not return
Markdown, explanations, or chain-of-thought.

The application layer, not the model, performs actions. For tools marked as
requiring confirmation, select the tool normally and let the application layer
handle the confirmation before execution.

If no available tool can satisfy the request, use "unknown_request" and give a
short explanation in the response field.
"""


def build_decision_schema(tool_descriptions: list[dict]) -> dict:
    """Build a JSON schema accepted by Ollama structured output."""
    tool_names = [item["name"] for item in tool_descriptions]
    tool_names.append("unknown_request")

    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "tool": {
                "type": "string",
                "enum": tool_names,
            },
            "arguments": {
                "type": "object",
                "additionalProperties": True,
            },
            "response": {
                "type": "string",
            },
        },
        "required": ["tool", "arguments", "response"],
    }


def build_user_input(
    command: str,
    context: str = "",
    tool_descriptions: list[dict] | None = None,
) -> str:
    """Build the model input without exposing Python handlers."""
    tools = tool_descriptions or []

    return (
        "Available JARVIS tools:\n"
        f"{tools}\n\n"
        "Recent conversation context:\n"
        f"{context or '(none)'}\n\n"
        "User request:\n"
        f"{command.strip()}"
    )
