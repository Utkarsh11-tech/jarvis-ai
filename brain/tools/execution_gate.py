"""
JARVIS Tool Execution Gate

Provides the safety boundary between a validated ToolSelection
and actual tool execution.

Responsibilities:
    - Resolve the selected tool through ToolRegistry.
    - Respect the registry's confirmation metadata.
    - Execute safe tools immediately.
    - Refuse confirmation-required tools without explicit confirmation.
    - Execute confirmation-required tools only after explicit confirmation.

This module does NOT:
    - call Ollama
    - call XTTS
    - ask the user for input
    - modify Assistant V2
    - modify the ToolRegistry
    - bypass confirmation metadata
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from brain.tools.registry import ToolRegistry
from brain.tools.tool_selector import ToolSelection

# ==========================================================
# EXECUTION RESULT
# ==========================================================


@dataclass(frozen=True)
class ToolExecutionResult:
    """
    Structured result returned by the execution gate.

    status:
        "executed"
        "confirmation_required"
        "cancelled"

    tool_name:
        Name of the selected capability.

    result:
        Actual handler result when execution occurred.
    """

    status: str
    tool_name: str
    result: Any = None


# ==========================================================
# EXECUTION GATE
# ==========================================================


def execute_selection(
    registry: ToolRegistry,
    selection: ToolSelection,
    confirmation: bool | None = None,
) -> ToolExecutionResult:
    """
    Execute a validated ToolSelection through the registry.

    Safe capabilities execute immediately.

    Confirmation-required capabilities:
        - return "confirmation_required" when confirmation is None
        - execute when confirmation is True
        - return "cancelled" when confirmation is False

    The confirmation requirement is always read from the
    registered ToolDefinition.

    The LLM cannot override the registry's policy.
    """

    if not isinstance(
        registry,
        ToolRegistry,
    ):
        raise TypeError("registry must be a ToolRegistry instance.")

    if not isinstance(
        selection,
        ToolSelection,
    ):
        raise TypeError("selection must be a ToolSelection instance.")

    if selection.kind != "tool":
        raise ValueError("Only tool selections can be executed.")

    if not selection.tool_name:
        raise ValueError("Tool selection does not contain a tool name.")

    arguments = selection.arguments or {}

    tool = registry.require(
        selection.tool_name,
    )

    # ------------------------------------------------------
    # CONFIRMATION GATE
    # ------------------------------------------------------

    if tool.requires_confirmation:

        if confirmation is None:

            return ToolExecutionResult(
                status="confirmation_required",
                tool_name=tool.name,
            )

        if confirmation is False:

            return ToolExecutionResult(
                status="cancelled",
                tool_name=tool.name,
            )

    # ------------------------------------------------------
    # EXECUTION
    # ------------------------------------------------------

    result = tool.handler(
        **arguments,
    )

    return ToolExecutionResult(
        status="executed",
        tool_name=tool.name,
        result=result,
    )
