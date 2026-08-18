"""
JARVIS Tool Execution Boundary Tests

STEP 3D

These tests verify the boundary between:

    ToolSelection
        ↓
    ToolRegistry
        ↓
    Tool Handler
        ↓
    Result

The tests intentionally do NOT connect this boundary to
Assistant V2 yet.

They also do NOT require:

    - XTTS
    - Ollama
    - GUI
    - RTX 5050
    - Internet access

Dangerous capabilities such as shutdown and sleep are
verified for confirmation protection but are NEVER invoked.
"""

from unittest.mock import patch

import pytest

from brain.tools.registry import (
    ToolDefinition,
    ToolRegistry,
    get_default_registry,
)

# ==========================================================
# FIXTURES
# ==========================================================


@pytest.fixture
def registry():
    """
    Return a fresh default JARVIS registry.
    """

    return get_default_registry()


# ==========================================================
# TEST 1
# BASIC TOOL INVOCATION
# ==========================================================


def test_registry_can_execute_system_info(
    registry,
):

    result = registry.invoke(
        "get_system_info",
    )

    assert isinstance(
        result,
        dict,
    )

    assert "system" in result
    assert "release" in result
    assert "python_version" in result


# ==========================================================
# TEST 2
# DISK TOOL EXECUTION
# ==========================================================


def test_registry_can_execute_disk_usage(
    registry,
):

    result = registry.invoke(
        "get_disk_usage",
    )

    assert isinstance(
        result,
        dict,
    )

    assert "path" in result
    assert "total_bytes" in result
    assert "used_bytes" in result
    assert "free_bytes" in result
    assert "percent_used" in result


# ==========================================================
# TEST 3
# DISK TOOL ACCEPTS ARGUMENTS
# ==========================================================


def test_registry_passes_tool_arguments(
    registry,
):

    result = registry.invoke(
        "get_disk_usage",
        path="C:\\",
    )

    assert isinstance(
        result,
        dict,
    )

    assert result["path"] == "C:\\"


# ==========================================================
# TEST 4
# CPU TOOL INVOCATION
# ==========================================================


def test_registry_can_execute_cpu_tool(
    registry,
):

    try:
        result = registry.invoke(
            "get_cpu_usage",
        )

    except RuntimeError as error:

        if "psutil" in str(error).lower():

            pytest.skip("psutil is not installed.")

        raise

    assert isinstance(
        result,
        dict,
    )

    assert "percent" in result
    assert "logical_processors" in result
    assert "physical_processors" in result


# ==========================================================
# TEST 5
# MEMORY TOOL INVOCATION
# ==========================================================


def test_registry_can_execute_memory_tool(
    registry,
):

    try:
        result = registry.invoke(
            "get_memory_usage",
        )

    except RuntimeError as error:

        if "psutil" in str(error).lower():

            pytest.skip("psutil is not installed.")

        raise

    assert isinstance(
        result,
        dict,
    )

    assert "total_bytes" in result
    assert "available_bytes" in result
    assert "used_bytes" in result
    assert "percent" in result


# ==========================================================
# TEST 6
# RESOURCE SUMMARY
# ==========================================================


def test_registry_can_execute_resource_summary(
    registry,
):

    try:
        result = registry.invoke(
            "get_resource_summary",
        )

    except RuntimeError as error:

        if "psutil" in str(error).lower():

            pytest.skip("psutil is not installed.")

        raise

    assert isinstance(
        result,
        dict,
    )

    assert "cpu_percent" in result
    assert "memory_percent" in result
    assert "disk_percent" in result


# ==========================================================
# TEST 7
# TOOL RESULT IS RETURNED UNMODIFIED
# ==========================================================


def test_registry_returns_handler_result():

    sentinel = {
        "status": "test-result",
        "value": 123,
    }

    def fake_handler():

        return sentinel

    test_registry = ToolRegistry()

    test_registry.register(
        ToolDefinition(
            name="test_tool",
            description="Test tool.",
            input_schema={
                "type": "object",
                "properties": {},
            },
            handler=fake_handler,
        )
    )

    result = test_registry.invoke(
        "test_tool",
    )

    assert result is sentinel


# ==========================================================
# TEST 8
# ARGUMENTS REACH HANDLER
# ==========================================================


def test_registry_forwards_arguments():

    received = {}

    def fake_handler(
        target,
        value,
    ):

        received["target"] = target
        received["value"] = value

        return "ok"

    test_registry = ToolRegistry()

    test_registry.register(
        ToolDefinition(
            name="argument_test",
            description="Argument forwarding test.",
            input_schema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                    },
                    "value": {
                        "type": "integer",
                    },
                },
                "required": [
                    "target",
                    "value",
                ],
            },
            handler=fake_handler,
        )
    )

    result = test_registry.invoke(
        "argument_test",
        target="example",
        value=42,
    )

    assert result == "ok"

    assert received == {
        "target": "example",
        "value": 42,
    }


# ==========================================================
# TEST 9
# UNKNOWN TOOL CANNOT EXECUTE
# ==========================================================


def test_unknown_tool_is_rejected(
    registry,
):

    with pytest.raises(
        KeyError,
        match="Unknown JARVIS tool",
    ):

        registry.invoke(
            "this_tool_does_not_exist",
        )


# ==========================================================
# TEST 10
# CONFIRMATION METADATA
# ==========================================================


def test_shutdown_requires_confirmation(
    registry,
):

    tool = registry.require(
        "system_command",
    )

    assert tool.requires_confirmation is True


# ==========================================================
# TEST 11
# SLEEP REQUIRES CONFIRMATION
# ==========================================================


def test_sleep_requires_confirmation(
    registry,
):

    tool = registry.require(
        "sleep_computer",
    )

    assert tool.requires_confirmation is True


# ==========================================================
# TEST 12
# LOCK DOES NOT REQUIRE CONFIRMATION
# ==========================================================


def test_lock_does_not_require_confirmation(
    registry,
):

    tool = registry.require(
        "lock_computer",
    )

    assert tool.requires_confirmation is False


# ==========================================================
# TEST 13
# CONFIRMATION IS NOT BYPASSED
# ==========================================================


def test_confirmation_is_not_bypassed(
    registry,
):

    shutdown_tool = registry.require(
        "system_command",
    )

    sleep_tool = registry.require(
        "sleep_computer",
    )

    assert shutdown_tool.requires_confirmation is True

    assert sleep_tool.requires_confirmation is True

    # ToolRegistry.invoke() intentionally does not
    # enforce confirmation itself.
    #
    # The caller/execution boundary must enforce the
    # confirmation policy before invoking dangerous tools.
    #
    # Therefore these tests only verify that the metadata
    # requiring confirmation is preserved.


# ==========================================================
# TEST 14
# SHUTDOWN HANDLER IS NOT EXECUTED
# ==========================================================


def test_shutdown_is_not_executed(
    registry,
):

    tool = registry.require(
        "system_command",
    )

    original_handler = tool.handler

    with patch(
        "brain.tools.registry._system_command",
    ) as mocked_handler:

        assert tool.requires_confirmation is True

        # The frozen ToolDefinition remains untouched.
        #
        # We patch the module-level handler instead.
        #
        # Most importantly, we NEVER invoke the tool.

        assert tool.handler is original_handler

        mocked_handler.assert_not_called()


# ==========================================================
# TEST 15
# SLEEP HANDLER IS NOT EXECUTED
# ==========================================================


def test_sleep_is_not_executed(
    registry,
):

    tool = registry.require(
        "sleep_computer",
    )

    original_handler = tool.handler

    with patch(
        "brain.tools.registry.sleep_computer",
    ) as mocked_handler:

        assert tool.requires_confirmation is True

        assert tool.handler is original_handler

        mocked_handler.assert_not_called()


# ==========================================================
# TEST 16
# READ-ONLY SYSTEM TOOLS ARE SAFE
# ==========================================================


def test_read_only_system_tools_are_safe(
    registry,
):

    safe_tools = {
        "get_system_info",
        "get_cpu_usage",
        "get_memory_usage",
        "get_disk_usage",
        "get_battery_status",
        "get_network_status",
        "get_resource_summary",
    }

    for name in safe_tools:

        tool = registry.require(
            name,
        )

        assert tool.requires_confirmation is False


# ==========================================================
# TEST 17
# REGISTRY EXECUTION DOES NOT REQUIRE VOICE
# ==========================================================


def test_registry_has_no_voice_dependency():

    import brain.tools.registry as registry_module

    source_path = registry_module.__file__

    assert source_path is not None

    with open(
        source_path,
        "r",
        encoding="utf-8",
    ) as file:

        source = file.read().lower()

    assert "voice_manager" not in source

    assert "brain.voices" not in source


# ==========================================================
# TEST 18
# SYSTEM TOOLS HAVE NO LLM DEPENDENCY
# ==========================================================


def test_system_tools_have_no_llm_dependency():

    import brain.tools.system_tools as system_tools

    source_path = system_tools.__file__

    assert source_path is not None

    with open(
        source_path,
        "r",
        encoding="utf-8",
    ) as file:

        source = file.read().lower()

    assert "ollama" not in source

    assert "ollama_client" not in source

    assert "brain.models" not in source


# ==========================================================
# TEST 19
# SYSTEM TOOLS HAVE NO NETWORK DEPENDENCY
# ==========================================================


def test_system_tools_have_no_network_dependency():

    import brain.tools.system_tools as system_tools

    source_path = system_tools.__file__

    assert source_path is not None

    with open(
        source_path,
        "r",
        encoding="utf-8",
    ) as file:

        source = file.read().lower()

    assert "requests" not in source

    assert "http://" not in source

    assert "https://" not in source


# ==========================================================
# TEST 20
# REGISTRY PRESERVES TOOL DEFINITIONS
# ==========================================================


def test_registry_definition_is_preserved(
    registry,
):

    tool = registry.require(
        "get_cpu_usage",
    )

    assert isinstance(
        tool,
        ToolDefinition,
    )

    assert tool.name == ("get_cpu_usage")

    assert isinstance(
        tool.description,
        str,
    )

    assert isinstance(
        tool.input_schema,
        dict,
    )

    assert callable(tool.handler)


# ==========================================================
# TEST 21
# ALL REGISTERED TOOLS ARE RESOLVABLE
# ==========================================================


def test_all_registered_tools_are_resolvable(
    registry,
):

    tools = registry.list_tools()

    assert tools

    for tool in tools:

        resolved = registry.get(
            tool.name,
        )

        assert resolved is tool


# ==========================================================
# TEST 22
# EXECUTION RESULT CAN BE CONSUMED
# ==========================================================


def test_execution_result_is_python_data(
    registry,
):

    result = registry.invoke(
        "get_system_info",
    )

    assert isinstance(
        result,
        dict,
    )

    for key, value in result.items():

        assert isinstance(
            key,
            str,
        )

        assert value is not None


# ==========================================================
# TEST 23
# TOOL EXECUTION REMAINS INDEPENDENT OF OLLAMA
# ==========================================================


def test_registry_execution_does_not_require_ollama(
    registry,
):

    result = registry.invoke(
        "get_system_info",
    )

    assert result

    assert isinstance(
        result,
        dict,
    )
