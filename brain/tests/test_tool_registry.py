"""Tests for the JARVIS tool registry."""

from brain.tools.registry import ToolDefinition, ToolRegistry, get_default_registry


def test_registry_register_and_lookup():
    registry = ToolRegistry()
    handler = lambda value: value

    registry.register(
        ToolDefinition(
            name="echo",
            description="Return a value.",
            input_schema={"type": "object"},
            handler=handler,
        )
    )

    assert registry.get("echo") is not None
    assert registry.require("echo").handler is handler
    assert registry.invoke("echo", value="hello") == "hello"


def test_default_registry_contains_expected_tools():
    registry = get_default_registry()
    names = {tool.name for tool in registry.list_tools()}

    assert names == {
        "file_search",
        "open_application",
        "play_media",
        "system_command",
        "ui_automation",
        "web_search",
    }


def test_system_tool_requires_confirmation():
    registry = get_default_registry()

    assert registry.require("system_command").requires_confirmation is True


def test_describe_hides_python_handlers():
    registry = get_default_registry()
    descriptions = registry.describe()

    assert descriptions
    assert all("handler" not in item for item in descriptions)
    assert all("name" in item and "input_schema" in item for item in descriptions)
