"""
JARVIS Tool Registry Tests

Step 2B:
Validate that the existing registry continues to work while the
new offline system capabilities are registered alongside it.

These tests do not require:
    - XTTS
    - Ollama
    - RTX 5050
    - internet access
"""

from brain.tools.registry import (
    ToolDefinition,
    ToolRegistry,
    get_default_registry,
)

# ==========================================================
# TEST 1
# REGISTRATION AND LOOKUP
# ==========================================================


def test_registry_register_and_lookup():

    registry = ToolRegistry()

    tool = ToolDefinition(
        name="test_tool",
        description="Test capability.",
        input_schema={
            "type": "object",
            "properties": {},
        },
        handler=lambda: "ok",
    )

    registry.register(tool)

    assert registry.get("test_tool") is tool

    assert registry.require("test_tool") is tool


# ==========================================================
# TEST 2
# UNKNOWN TOOL
# ==========================================================


def test_registry_unknown_tool():

    registry = ToolRegistry()

    assert registry.get("does_not_exist") is None

    try:
        registry.require("does_not_exist")

    except KeyError as error:

        assert "Unknown JARVIS tool" in str(error)

    else:

        raise AssertionError("Unknown tool did not raise KeyError.")


# ==========================================================
# TEST 3
# DUPLICATE REGISTRATION
# ==========================================================


def test_registry_rejects_duplicate_tools():

    registry = ToolRegistry()

    tool = ToolDefinition(
        name="duplicate",
        description="Duplicate test.",
        input_schema={
            "type": "object",
            "properties": {},
        },
        handler=lambda: None,
    )

    registry.register(tool)

    try:

        registry.register(tool)

    except ValueError as error:

        assert "already registered" in str(error)

    else:

        raise AssertionError("Duplicate registration was accepted.")


# ==========================================================
# TEST 4
# DEFAULT REGISTRY
# ==========================================================


def test_default_registry_contains_expected_tools():

    registry = get_default_registry()

    expected_tools = {
        # Existing tools
        "open_application",
        "play_media",
        "web_search",
        "file_search",
        "ui_automation",
        "system_command",
        # New system tools
        "get_system_info",
        "get_cpu_usage",
        "get_memory_usage",
        "get_disk_usage",
        "get_battery_status",
        "get_network_status",
        "get_resource_summary",
        "lock_computer",
        "sleep_computer",
    }

    actual_tools = {tool.name for tool in registry.list_tools()}

    assert actual_tools == expected_tools


# ==========================================================
# TEST 5
# TOOL COUNT
# ==========================================================


def test_default_registry_tool_count():

    registry = get_default_registry()

    assert len(registry.list_tools()) == 15


# ==========================================================
# TEST 6
# SYSTEM INFO TOOL
# ==========================================================


def test_system_info_tool_is_registered():

    registry = get_default_registry()

    tool = registry.require("get_system_info")

    assert tool.name == ("get_system_info")

    assert callable(tool.handler)

    assert tool.requires_confirmation is False


# ==========================================================
# TEST 7
# SYSTEM INFO TOOL INVOCATION
# ==========================================================


def test_system_info_tool_can_be_invoked():

    registry = get_default_registry()

    result = registry.invoke("get_system_info")

    assert isinstance(
        result,
        dict,
    )

    assert "system" in result
    assert "python_version" in result


# ==========================================================
# TEST 8
# DISK TOOL INVOCATION
# ==========================================================


def test_disk_tool_can_be_invoked(
    tmp_path,
):

    registry = get_default_registry()

    result = registry.invoke(
        "get_disk_usage",
        path=str(tmp_path),
    )

    assert isinstance(
        result,
        dict,
    )

    assert result["path"] == str(tmp_path)

    assert result["total_bytes"] > 0


# ==========================================================
# TEST 9
# SYSTEM COMMAND CONFIRMATION
# ==========================================================


def test_system_tool_requires_confirmation():

    registry = get_default_registry()

    tool = registry.require("system_command")

    assert tool.requires_confirmation is True


# ==========================================================
# TEST 10
# SLEEP REQUIRES CONFIRMATION
# ==========================================================


def test_sleep_requires_confirmation():

    registry = get_default_registry()

    tool = registry.require("sleep_computer")

    assert tool.requires_confirmation is True


# ==========================================================
# TEST 11
# LOCK DOES NOT REQUIRE CONFIRMATION
# ==========================================================


def test_lock_does_not_require_confirmation():

    registry = get_default_registry()

    tool = registry.require("lock_computer")

    assert tool.requires_confirmation is False


# ==========================================================
# TEST 12
# DESCRIBE HIDES HANDLERS
# ==========================================================


def test_describe_hides_python_handlers():

    registry = get_default_registry()

    descriptions = registry.describe()

    assert len(descriptions) == 15

    for description in descriptions:

        assert "name" in description
        assert "description" in description
        assert "input_schema" in description
        assert "requires_confirmation" in description

        assert "handler" not in description


# ==========================================================
# TEST 13
# TOOL ORDER IS DETERMINISTIC
# ==========================================================


def test_tool_listing_is_sorted():

    registry = get_default_registry()

    names = [tool.name for tool in registry.list_tools()]

    assert names == sorted(names)


# ==========================================================
# TEST 14
# ALL DESCRIPTIONS ARE LLM-SAFE
# ==========================================================


def test_all_tool_descriptions_are_serializable():

    registry = get_default_registry()

    descriptions = registry.describe()

    for description in descriptions:

        assert isinstance(
            description["name"],
            str,
        )

        assert isinstance(
            description["description"],
            str,
        )

        assert isinstance(
            description["input_schema"],
            dict,
        )

        assert isinstance(
            description["requires_confirmation"],
            bool,
        )


# ==========================================================
# TEST 15
# SYSTEM TOOLS ARE NOT VOICE DEPENDENT
# ==========================================================


def test_registry_system_tools_do_not_require_voice():

    registry = get_default_registry()

    system_tool_names = {
        "get_system_info",
        "get_cpu_usage",
        "get_memory_usage",
        "get_disk_usage",
        "get_battery_status",
        "get_network_status",
        "get_resource_summary",
        "lock_computer",
        "sleep_computer",
    }

    for name in system_tool_names:

        tool = registry.require(name)

        assert callable(tool.handler)


# ==========================================================
# TEST 16
# NO DANGEROUS TOOL IS ADDED ACCIDENTALLY
# ==========================================================


def test_no_permanent_delete_tool_exists():

    registry = get_default_registry()

    forbidden_names = {
        "permanent_delete",
        "delete_permanently",
        "secure_delete",
        "wipe_file",
        "wipe_disk",
    }

    actual_names = {tool.name for tool in registry.list_tools()}

    assert actual_names.isdisjoint(forbidden_names)
