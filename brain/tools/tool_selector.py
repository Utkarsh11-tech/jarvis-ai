"""
JARVIS Tool Selector

Provides the boundary between the JARVIS LLM and the Tool Registry.

Responsibilities:
    - Present available capabilities to the LLM.
    - Ask the LLM to select either a capability or normal conversation.
    - Parse the LLM response.
    - Validate selected capabilities against the ToolRegistry.
    - Validate tool arguments against the registered input schema.

This module does NOT:
    - execute tools
    - call tool handlers
    - call XTTS
    - modify the ToolRegistry
    - modify Assistant V2
    - perform operating-system actions

Execution belongs to a later stage.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol

from brain.tools.capabilities import (
    build_capability_document,
)
from brain.tools.registry import (
    ToolRegistry,
)

# ==========================================================
# SELECTION RESULT
# ==========================================================


@dataclass(frozen=True)
class ToolSelection:
    """
    Validated result returned by the tool-selection layer.

    kind:
        "tool" or "conversation"

    tool_name:
        Registered capability name when kind == "tool".

    arguments:
        Validated arguments for the selected capability.

    response:
        Conversational response when kind == "conversation".
    """

    kind: str
    tool_name: str | None = None
    arguments: dict[str, Any] | None = None
    response: str | None = None


# ==========================================================
# LLM PROTOCOL
# ==========================================================


class LLMClient(Protocol):
    """
    Minimal interface required from an LLM client.

    This keeps the selector independent of Ollama itself and
    makes the selector easy to test with a fake client.
    """

    def generate(
        self,
        prompt: str,
        system_prompt: str,
        history: list[dict[str, Any]] | None = None,
    ) -> str: ...


# ==========================================================
# SYSTEM PROMPT
# ==========================================================


TOOL_SELECTOR_SYSTEM_PROMPT = """
You are the JARVIS capability-selection layer.

Your job is to decide whether the user's request should be:

1. Normal conversation.
2. A call to one registered JARVIS capability.

You MUST follow these rules:

- Only select capabilities that appear in the supplied capability list.
- Never invent a capability name.
- Never invent additional capability behavior.
- Never execute a capability.
- Never return Python code.
- Never return shell commands.
- Never return executable instructions.
- Return exactly one JSON object.
- Do not wrap the JSON in Markdown.
- Do not add explanations outside the JSON.

For normal conversation, return:

{
    "type": "conversation",
    "response": "your response"
}

For a capability request, return:

{
    "type": "tool_call",
    "tool": "registered_tool_name",
    "arguments": {}
}

If a capability requires arguments, provide them inside
the arguments object according to its registered schema.

The capability list is authoritative.
""".strip()


# ==========================================================
# PROMPT BUILDER
# ==========================================================


def build_tool_selection_prompt(
    registry: ToolRegistry,
    command: str,
) -> str:
    """
    Build the prompt supplied to the LLM for capability
    selection.

    This function only builds text.

    No capability is executed.
    """

    if not isinstance(
        registry,
        ToolRegistry,
    ):
        raise TypeError("registry must be a ToolRegistry instance.")

    if not isinstance(
        command,
        str,
    ):
        raise TypeError("command must be a string.")

    command = command.strip()

    if not command:
        raise ValueError("command cannot be empty.")

    capability_document = build_capability_document(registry)

    capability_json = json.dumps(
        capability_document,
        ensure_ascii=False,
        indent=2,
    )

    return (
        "Available JARVIS capabilities:\n\n"
        f"{capability_json}\n\n"
        "User request:\n"
        f"{command}\n\n"
        "Return exactly one JSON object following "
        "the required selection format."
    )


# ==========================================================
# JSON EXTRACTION
# ==========================================================


def _extract_json_object(
    response: str,
) -> dict[str, Any]:
    """
    Parse one JSON object from an LLM response.

    Markdown fences and surrounding whitespace are tolerated,
    but the resulting payload must still be a JSON object.
    """

    if not isinstance(
        response,
        str,
    ):
        raise TypeError("LLM response must be a string.")

    cleaned = response.strip()

    if not cleaned:
        raise ValueError("LLM response is empty.")

    # ------------------------------------------------------
    # Remove optional Markdown code fences.
    # ------------------------------------------------------

    if cleaned.startswith("```"):

        lines = cleaned.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

    # ------------------------------------------------------
    # First attempt: complete JSON object.
    # ------------------------------------------------------

    try:

        payload = json.loads(cleaned)

    except json.JSONDecodeError:

        # --------------------------------------------------
        # Second attempt: locate the first JSON object.
        # --------------------------------------------------

        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start == -1 or end == -1 or end <= start:

            raise ValueError("LLM response does not contain a JSON object.")

        candidate = cleaned[start : end + 1]

        try:

            payload = json.loads(candidate)

        except json.JSONDecodeError as error:

            raise ValueError("LLM response contains invalid JSON.") from error

    if not isinstance(
        payload,
        dict,
    ):

        raise ValueError("LLM response must contain a JSON object.")

    return payload


# ==========================================================
# ARGUMENT VALIDATION
# ==========================================================


def _validate_arguments(
    tool_name: str,
    arguments: Any,
    schema: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate tool arguments against the registered schema.

    This intentionally performs structural validation only.

    Actual tool execution is handled elsewhere.
    """

    if arguments is None:
        arguments = {}

    if not isinstance(
        arguments,
        dict,
    ):

        raise ValueError(f"Arguments for '{tool_name}' must be an object.")

    properties = schema.get(
        "properties",
        {},
    )

    required = schema.get(
        "required",
        [],
    )

    # ------------------------------------------------------
    # Required arguments
    # ------------------------------------------------------

    for name in required:

        if name not in arguments:

            raise ValueError(
                f"Missing required argument " f"'{name}' for tool '{tool_name}'."
            )

    # ------------------------------------------------------
    # Unknown arguments
    # ------------------------------------------------------

    for name in arguments:

        if name not in properties:

            raise ValueError(f"Unknown argument '{name}' " f"for tool '{tool_name}'.")

    # ------------------------------------------------------
    # Basic type validation
    # ------------------------------------------------------

    for name, value in arguments.items():

        property_schema = properties[name]

        expected_type = property_schema.get("type")

        if expected_type is None:
            continue

        allowed_types = (
            expected_type
            if isinstance(
                expected_type,
                list,
            )
            else [expected_type]
        )

        if not _matches_schema_type(
            value,
            allowed_types,
        ):

            raise ValueError(
                f"Invalid type for argument " f"'{name}' of tool '{tool_name}'."
            )

        enum = property_schema.get("enum")

        if enum is not None and value not in enum:

            raise ValueError(
                f"Invalid value for argument " f"'{name}' of tool '{tool_name}'."
            )

    return dict(arguments)


def _matches_schema_type(
    value: Any,
    allowed_types: list[str],
) -> bool:
    """
    Perform basic JSON-schema-compatible type checking.
    """

    for expected_type in allowed_types:

        if expected_type == "null":
            if value is None:
                return True

        elif expected_type == "string":
            if isinstance(
                value,
                str,
            ):
                return True

        elif expected_type == "object":
            if isinstance(
                value,
                dict,
            ):
                return True

        elif expected_type == "array":
            if isinstance(
                value,
                list,
            ):
                return True

        elif expected_type == "boolean":
            if isinstance(
                value,
                bool,
            ):
                return True

        elif expected_type == "integer":
            if isinstance(
                value,
                int,
            ) and not isinstance(
                value,
                bool,
            ):
                return True

        elif expected_type == "number":
            if isinstance(
                value,
                (
                    int,
                    float,
                ),
            ) and not isinstance(
                value,
                bool,
            ):
                return True

    return False


# ==========================================================
# SELECTION VALIDATION
# ==========================================================


def validate_selection(
    registry: ToolRegistry,
    payload: dict[str, Any],
) -> ToolSelection:
    """
    Validate an LLM selection against the ToolRegistry.

    No tool is executed.
    """

    if not isinstance(
        registry,
        ToolRegistry,
    ):
        raise TypeError("registry must be a ToolRegistry instance.")

    if not isinstance(
        payload,
        dict,
    ):
        raise TypeError("payload must be a dictionary.")

    selection_type = payload.get("type")

    # ======================================================
    # NORMAL CONVERSATION
    # ======================================================

    if selection_type == "conversation":

        response = payload.get("response")

        if not isinstance(
            response,
            str,
        ):

            raise ValueError("Conversation response must be a string.")

        response = response.strip()

        if not response:

            raise ValueError("Conversation response cannot be empty.")

        return ToolSelection(
            kind="conversation",
            response=response,
        )

    # ======================================================
    # TOOL CALL
    # ======================================================

    if selection_type == "tool_call":

        tool_name = payload.get("tool")

        if not isinstance(
            tool_name,
            str,
        ):

            raise ValueError("Tool name must be a string.")

        tool_name = tool_name.strip()

        if not tool_name:

            raise ValueError("Tool name cannot be empty.")

        tool = registry.get(tool_name)

        if tool is None:

            raise ValueError(f"Unknown JARVIS tool: {tool_name}")

        arguments = _validate_arguments(
            tool_name,
            payload.get(
                "arguments",
                {},
            ),
            tool.input_schema,
        )

        return ToolSelection(
            kind="tool",
            tool_name=tool_name,
            arguments=arguments,
        )

    # ======================================================
    # INVALID TYPE
    # ======================================================

    raise ValueError("Selection type must be " "'conversation' or 'tool_call'.")


# ==========================================================
# PARSE SELECTION
# ==========================================================


def parse_tool_selection(
    registry: ToolRegistry,
    response: str,
) -> ToolSelection:
    """
    Parse and validate an LLM selection response.

    No tool is executed.
    """

    payload = _extract_json_object(response)

    return validate_selection(
        registry,
        payload,
    )


# ==========================================================
# LLM SELECTION
# ==========================================================


def select_tool(
    llm: LLMClient,
    registry: ToolRegistry,
    command: str,
    history: list[dict[str, Any]] | None = None,
) -> ToolSelection:
    """
    Ask the LLM to classify/select a JARVIS capability.

    Returns a validated ToolSelection.

    This function does NOT invoke the selected capability.
    """

    if llm is None:
        raise ValueError("llm cannot be None.")

    prompt = build_tool_selection_prompt(
        registry,
        command,
    )

    response = llm.generate(
        prompt=prompt,
        system_prompt=(TOOL_SELECTOR_SYSTEM_PROMPT),
        history=history or [],
    )

    return parse_tool_selection(
        registry,
        response,
    )
