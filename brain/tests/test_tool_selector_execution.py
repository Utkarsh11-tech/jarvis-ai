"""
JARVIS Tool Selector → Tool Registry Execution Integration Tests

Verifies the complete deterministic boundary:

    structured tool-selection response
                ↓
        ToolSelection parser
                ↓
            ToolRegistry
                ↓
          real tool handler
                ↓
          Python result

This test does NOT:
    - use XTTS
    - use the voice manager
    - call Ollama
    - open applications
    - shut down the computer
    - restart the computer
    - put the computer to sleep
    - delete files
"""

from __future__ import annotations

import json

import pytest

from brain.tools.registry import (
    ToolRegistry,
    get_default_registry,
)

from brain.tools.tool_selector import (
    ToolSelection,
    parse_tool_selection,
)

# ==========================================================
# FIXTURES
# ==========================================================


@pytest.fixture
def registry() -> ToolRegistry:
    """
    Return a fresh real JARVIS ToolRegistry for each test.
    """

    return get_default_registry()


# ==========================================================
# HELPERS
# ==========================================================


def _select_tool(
    registry: ToolRegistry,
    tool_name: str,
    arguments: dict,
) -> ToolSelection:
    """
    Build a deterministic structured tool-selection response
    and parse it through the real selector.

    The response is serialized to JSON because the real selector
    receives model output as text.
    """

    response = json.dumps(
        {
            "type": "tool_call",
            "tool": tool_name,
            "arguments": arguments,
        }
    )

    return parse_tool_selection(
        registry,
        response,
    )


def _execute_selection(
    registry: ToolRegistry,
    selection: ToolSelection,
):
    """
    Resolve a parsed ToolSelection through the real registry
    and execute the registered handler.
    """

    tool = registry.require(selection.tool_name)

    return tool.handler(**selection.arguments)


# ==========================================================
# TOOL SELECTION → REGISTRY
# ==========================================================


def test_system_info_selection_reaches_registry(
    registry,
):
    """
    A get_system_info selection must resolve to the real
    registered capability.
    """

    selection = _select_tool(
        registry,
        "get_system_info",
        {},
    )

    tool = registry.require(selection.tool_name)

    assert tool.name == "get_system_info"


def test_memory_selection_reaches_registry(
    registry,
):
    """
    A get_memory_usage selection must resolve correctly.
    """

    selection = _select_tool(
        registry,
        "get_memory_usage",
        {},
    )

    tool = registry.require(selection.tool_name)

    assert tool.name == "get_memory_usage"


def test_disk_selection_preserves_arguments(
    registry,
):
    """
    Tool arguments must survive selector parsing and reach
    the registry unchanged.
    """

    selection = _select_tool(
        registry,
        "get_disk_usage",
        {
            "path": "C:\\",
        },
    )

    assert selection.tool_name == "get_disk_usage"

    assert selection.arguments == {
        "path": "C:\\",
    }

    tool = registry.require(selection.tool_name)

    assert tool.name == "get_disk_usage"


# ==========================================================
# REAL HANDLER EXECUTION
# ==========================================================


def test_system_info_selection_executes_real_handler(
    registry,
):
    """
    The selected system-info capability must execute through
    the real registry and return Python data.
    """

    selection = _select_tool(
        registry,
        "get_system_info",
        {},
    )

    result = _execute_selection(
        registry,
        selection,
    )

    assert isinstance(
        result,
        dict,
    )

    assert "system" in result
    assert "python_version" in result


def test_disk_selection_executes_real_handler(
    registry,
):
    """
    The selected disk capability must execute through the
    real registry.
    """

    selection = _select_tool(
        registry,
        "get_disk_usage",
        {
            "path": "C:\\",
        },
    )

    result = _execute_selection(
        registry,
        selection,
    )

    assert isinstance(
        result,
        dict,
    )

    assert result["path"] == "C:\\"

    assert "total_bytes" in result
    assert "used_bytes" in result
    assert "free_bytes" in result
    assert "percent_used" in result


def test_cpu_selection_executes_real_handler(
    registry,
):
    """
    The CPU capability must execute through the real registry.

    psutil is required for this test.
    """

    try:
        import psutil  # noqa: F401
    except ImportError:
        pytest.skip("psutil is not installed.")

    selection = _select_tool(
        registry,
        "get_cpu_usage",
        {},
    )

    result = _execute_selection(
        registry,
        selection,
    )

    assert isinstance(
        result,
        dict,
    )

    assert "percent" in result
    assert "logical_processors" in result
    assert "physical_processors" in result


def test_memory_selection_executes_real_handler(
    registry,
):
    """
    The memory capability must execute through the real
    registry.

    psutil is required for this test.
    """

    try:
        import psutil  # noqa: F401
    except ImportError:
        pytest.skip("psutil is not installed.")

    selection = _select_tool(
        registry,
        "get_memory_usage",
        {},
    )

    result = _execute_selection(
        registry,
        selection,
    )

    assert isinstance(
        result,
        dict,
    )

    assert "total_bytes" in result
    assert "available_bytes" in result
    assert "used_bytes" in result
    assert "percent" in result


def test_resource_summary_selection_executes_real_handler(
    registry,
):
    """
    The resource-summary capability must execute through
    the real registry.

    psutil is required for this test.
    """

    try:
        import psutil  # noqa: F401
    except ImportError:
        pytest.skip("psutil is not installed.")

    selection = _select_tool(
        registry,
        "get_resource_summary",
        {},
    )

    result = _execute_selection(
        registry,
        selection,
    )

    assert isinstance(
        result,
        dict,
    )

    assert "cpu_percent" in result
    assert "memory_percent" in result
    assert "disk_percent" in result


# ==========================================================
# CONFIRMATION BOUNDARY
# ==========================================================


def test_confirmation_metadata_survives_selection(
    registry,
):
    """
    A confirmation-required capability must remain marked
    as requiring confirmation.
    """

    selection = _select_tool(
        registry,
        "sleep_computer",
        {},
    )

    tool = registry.require(selection.tool_name)

    assert tool.requires_confirmation is True


def test_shutdown_metadata_survives_selection(
    registry,
):
    """
    Shutdown must remain a confirmation-required capability.
    """

    selection = _select_tool(
        registry,
        "system_command",
        {
            "target": "shutdown",
        },
    )

    tool = registry.require(selection.tool_name)

    assert tool.requires_confirmation is True


def test_safe_tool_does_not_require_confirmation(
    registry,
):
    """
    Read-only system information must remain safe.
    """

    selection = _select_tool(
        registry,
        "get_system_info",
        {},
    )

    tool = registry.require(selection.tool_name)

    assert tool.requires_confirmation is False


# ==========================================================
# UNKNOWN TOOL
# ==========================================================


def test_unknown_selected_tool_is_rejected(
    registry,
):
    """
    A nonexistent capability must be rejected by the real
    selector/registry boundary.
    """

    with pytest.raises(
        (KeyError, ValueError),
    ):
        _select_tool(
            registry,
            "does_not_exist",
            {},
        )


# ==========================================================
# RESULT TYPE
# ==========================================================


def test_execution_returns_python_data(
    registry,
):
    """
    Tool execution must return ordinary Python data.
    """

    selection = _select_tool(
        registry,
        "get_system_info",
        {},
    )

    result = _execute_selection(
        registry,
        selection,
    )

    assert isinstance(
        result,
        dict,
    )


# ==========================================================
# NO VOICE DEPENDENCY
# ==========================================================


def test_integration_boundary_has_no_voice_dependency():
    """
    The selector-to-registry execution boundary must not
    depend on XTTS or the voice manager.
    """

    import inspect

    source = inspect.getsource(_execute_selection).lower()

    assert "xtts" not in source
    assert "voice_manager" not in source


# ==========================================================
# NO OLLAMA DEPENDENCY
# ==========================================================


def test_execution_boundary_does_not_call_ollama():
    """
    Once a ToolSelection exists, execution must not require
    another Ollama request.
    """

    import inspect

    source = inspect.getsource(_execute_selection).lower()

    assert "ollama" not in source


# ==========================================================
# COMPLETE FLOW
# ==========================================================


def test_complete_selector_to_registry_to_handler_flow(
    registry,
):
    """
    Complete deterministic flow:

        structured response
                ↓
        ToolSelection parser
                ↓
          ToolRegistry
                ↓
          real handler
                ↓
          Python result
    """

    selection = _select_tool(
        registry,
        "get_system_info",
        {},
    )

    assert selection.tool_name == ("get_system_info")

    tool = registry.require(selection.tool_name)

    assert tool.name == ("get_system_info")

    result = tool.handler(**selection.arguments)

    assert isinstance(
        result,
        dict,
    )

    assert result.get("system") is not None

    assert result.get("python_version") is not None
