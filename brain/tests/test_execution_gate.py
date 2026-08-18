import pytest

from brain.tools.execution_gate import (
    ToolExecutionResult,
    execute_selection,
)
from brain.tools.registry import (
    ToolRegistry,
    get_default_registry,
)
from brain.tools.tool_selector import (
    ToolSelection,
)


@pytest.fixture
def registry():
    return get_default_registry()


def make_selection(
    tool_name,
    arguments=None,
):
    return ToolSelection(
        kind="tool",
        tool_name=tool_name,
        arguments=arguments or {},
    )


# ==========================================================
# SAFE TOOLS
# ==========================================================


def test_safe_tool_executes_without_confirmation(
    registry,
):
    selection = make_selection(
        "get_system_info",
    )

    result = execute_selection(
        registry,
        selection,
    )

    assert isinstance(
        result,
        ToolExecutionResult,
    )

    assert result.status == "executed"

    assert result.tool_name == "get_system_info"

    assert isinstance(
        result.result,
        dict,
    )


# ==========================================================
# CONFIRMATION REQUIRED
# ==========================================================


def test_confirmation_required_tool_does_not_execute_without_confirmation(
    registry,
):
    selection = make_selection(
        "sleep_computer",
    )

    tool = registry.require(
        "sleep_computer",
    )

    original_handler = tool.handler

    executed = False

    def fake_handler():
        nonlocal executed
        executed = True
        return "executed"

    object.__setattr__(
        tool,
        "handler",
        fake_handler,
    )

    try:

        result = execute_selection(
            registry,
            selection,
        )

        assert result.status == "confirmation_required"

        assert result.tool_name == "sleep_computer"

        assert executed is False

    finally:

        object.__setattr__(
            tool,
            "handler",
            original_handler,
        )


def test_confirmation_required_tool_executes_after_confirmation(
    registry,
):
    selection = make_selection(
        "sleep_computer",
    )

    tool = registry.require(
        "sleep_computer",
    )

    original_handler = tool.handler

    calls = []

    def fake_handler():
        calls.append(True)
        return "sleep requested"

    object.__setattr__(
        tool,
        "handler",
        fake_handler,
    )

    try:

        result = execute_selection(
            registry,
            selection,
            confirmation=True,
        )

        assert result.status == "executed"

        assert result.tool_name == "sleep_computer"

        assert result.result == "sleep requested"

        assert calls == [True]

    finally:

        object.__setattr__(
            tool,
            "handler",
            original_handler,
        )


def test_confirmation_required_tool_is_cancelled(
    registry,
):
    selection = make_selection(
        "sleep_computer",
    )

    tool = registry.require(
        "sleep_computer",
    )

    original_handler = tool.handler

    executed = False

    def fake_handler():
        nonlocal executed
        executed = True
        return "should not happen"

    object.__setattr__(
        tool,
        "handler",
        fake_handler,
    )

    try:

        result = execute_selection(
            registry,
            selection,
            confirmation=False,
        )

        assert result.status == "cancelled"

        assert result.tool_name == "sleep_computer"

        assert result.result is None

        assert executed is False

    finally:

        object.__setattr__(
            tool,
            "handler",
            original_handler,
        )


# ==========================================================
# UNKNOWN TOOL
# ==========================================================


def test_unknown_tool_is_rejected(
    registry,
):
    selection = make_selection(
        "does_not_exist",
    )

    with pytest.raises(KeyError):

        execute_selection(
            registry,
            selection,
        )


# ==========================================================
# INVALID SELECTION
# ==========================================================


def test_conversation_selection_cannot_execute(
    registry,
):
    selection = ToolSelection(
        kind="conversation",
        response="Hello.",
    )

    with pytest.raises(ValueError):

        execute_selection(
            registry,
            selection,
        )


# ==========================================================
# ARGUMENT FORWARDING
# ==========================================================


def test_arguments_reach_handler(
    registry,
):
    selection = make_selection(
        "get_disk_usage",
        {
            "path": "C:\\",
        },
    )

    result = execute_selection(
        registry,
        selection,
    )

    assert result.status == "executed"

    assert result.tool_name == "get_disk_usage"

    assert result.result["path"] == "C:\\"
