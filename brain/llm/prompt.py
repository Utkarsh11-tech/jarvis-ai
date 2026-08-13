"""System prompt and structured output schema for JARVIS."""

SYSTEM_PROMPT = """You are the reasoning layer of JARVIS, a desktop AI assistant.

Your job is to understand the user's request and select exactly one available
JARVIS tool. Never invent a tool. Never invent arguments that are not supported
by the selected tool schema.

Return a concise user-facing response describing what JARVIS will do. For
requests that require confirmation, the application layer will handle the
confirmation; do not execute the action yourself.

If the request cannot be fulfilled by an available tool, use the tool named
unknown_request.
"""


def build_decision_schema(tool_descriptions: list[dict]) -> dict:
    """Build the strict JSON schema accepted by the Responses API."""
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


def build_user_input(command: str, context: str = "", tool_descriptions: list[dict] | None = None) -> str:
    """Build the model input without exposing Python handlers."""
    tools = tool_descriptions or []

    return (
        "Available tools:\n"
        f"{tools}\n\n"
        "Recent conversation context:\n"
        f"{context or '(none)'}\n\n"
        "User request:\n"
        f"{command.strip()}"
    )
