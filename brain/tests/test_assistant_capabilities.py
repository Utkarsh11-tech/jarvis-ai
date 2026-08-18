"""
JARVIS Assistant Capability Awareness Tests

STEP 3A

Validates that Assistant V2 can expose the Tool Registry
through its LLM-safe capability document.

These tests do not require:
    - XTTS
    - Ollama
    - RTX 5050
    - internet access
    - GUI startup
"""

from brain.core import assistant_v2
from brain.tools.registry import (
    get_default_registry,
)

# ==========================================================
# TEST 1
# ASSISTANT HAS TOOL REGISTRY
# ==========================================================


def test_assistant_has_tool_registry():

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    assistant.tool_registry = get_default_registry()

    assert hasattr(
        assistant,
        "tool_registry",
    )

    assert assistant.tool_registry is not None


# ==========================================================
# TEST 2
# GET TOOL REGISTRY
# ==========================================================


def test_get_tool_registry():

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    registry = get_default_registry()

    assistant.tool_registry = registry

    result = assistant.get_tool_registry()

    assert result is registry


# ==========================================================
# TEST 3
# GET CAPABILITIES
# ==========================================================


def test_get_capabilities():

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    assistant.tool_registry = get_default_registry()

    capabilities = assistant.get_capabilities()

    assert isinstance(
        capabilities,
        dict,
    )

    assert capabilities["name"] == ("JARVIS")

    assert capabilities["capability_count"] == 15

    assert isinstance(
        capabilities["capabilities"],
        list,
    )


# ==========================================================
# TEST 4
# ALL REGISTERED TOOLS ARE EXPOSED
# ==========================================================


def test_all_registered_tools_are_exposed():

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    assistant.tool_registry = get_default_registry()

    capabilities = assistant.get_capabilities()

    registry_names = {tool.name for tool in assistant.tool_registry.list_tools()}

    capability_names = {
        capability["name"] for capability in capabilities["capabilities"]
    }

    assert capability_names == (registry_names)


# ==========================================================
# TEST 5
# CAPABILITY METADATA IS LLM SAFE
# ==========================================================


def test_capability_metadata_is_llm_safe():

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    assistant.tool_registry = get_default_registry()

    capabilities = assistant.get_capabilities()

    for capability in capabilities["capabilities"]:

        assert set(capability.keys()) == {
            "name",
            "description",
            "input_schema",
            "requires_confirmation",
        }

        assert "handler" not in (capability)


# ==========================================================
# TEST 6
# SYSTEM TOOL IS VISIBLE
# ==========================================================


def test_system_capabilities_are_visible():

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    assistant.tool_registry = get_default_registry()

    capabilities = assistant.get_capabilities()

    names = {capability["name"] for capability in capabilities["capabilities"]}

    assert "get_system_info" in names

    assert "get_cpu_usage" in names

    assert "get_memory_usage" in names

    assert "get_disk_usage" in names


# ==========================================================
# TEST 7
# CONFIRMATION METADATA IS PRESERVED
# ==========================================================


def test_confirmation_metadata_is_preserved():

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    assistant.tool_registry = get_default_registry()

    capabilities = assistant.get_capabilities()

    by_name = {
        capability["name"]: capability for capability in capabilities["capabilities"]
    }

    assert by_name["system_command"]["requires_confirmation"] is True

    assert by_name["sleep_computer"]["requires_confirmation"] is True

    assert by_name["get_system_info"]["requires_confirmation"] is False


# ==========================================================
# TEST 8
# CAPABILITY VIEW DOES NOT EXECUTE TOOLS
# ==========================================================


def test_get_capabilities_does_not_execute_tools():

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    registry = get_default_registry()

    assistant.tool_registry = registry

    invoked = []

    original_invoke = registry.invoke

    def tracking_invoke(
        name,
        **arguments,
    ):

        invoked.append(
            (
                name,
                arguments,
            )
        )

        return original_invoke(
            name,
            **arguments,
        )

    registry.invoke = tracking_invoke

    assistant.get_capabilities()

    assert invoked == []


# ==========================================================
# TEST 9
# CAPABILITY ACCESS DOES NOT REQUIRE OLLAMA
# ==========================================================


def test_capability_access_does_not_require_ollama():

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    assistant.tool_registry = get_default_registry()

    # Deliberately do NOT create:
    #
    # assistant.ollama
    #
    # Capability access must remain independent
    # from the LLM client.

    capabilities = assistant.get_capabilities()

    assert capabilities["capability_count"] == 15


# ==========================================================
# TEST 10
# CAPABILITY ACCESS DOES NOT REQUIRE XTTS
# ==========================================================


def test_capability_access_does_not_require_xtts():

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    assistant.tool_registry = get_default_registry()

    # Deliberately do NOT create or initialize
    # any voice backend.

    capabilities = assistant.get_capabilities()

    assert capabilities["capability_count"] == 15


# ==========================================================
# TEST 11
# REGISTRY REMAINS THE SOURCE OF TRUTH
# ==========================================================


def test_registry_is_source_of_truth():

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    registry = get_default_registry()

    assistant.tool_registry = registry

    before = assistant.get_capabilities()

    registry.register(
        __import__(
            "brain.tools.registry",
            fromlist=["ToolDefinition"],
        ).ToolDefinition(
            name="test_capability",
            description=("Temporary capability " "used only for testing."),
            input_schema={
                "type": "object",
                "properties": {},
            },
            handler=lambda: None,
        )
    )

    after = assistant.get_capabilities()

    assert before["capability_count"] == 15

    assert after["capability_count"] == 16

    assert any(
        capability["name"] == "test_capability" for capability in after["capabilities"]
    )


# ==========================================================
# TEST 12
# EXISTING REGISTRY OBJECT IS REUSED
# ==========================================================


def test_assistant_uses_existing_registry_object():

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    registry = get_default_registry()

    assistant.tool_registry = registry

    assert assistant.get_tool_registry() is registry

    assert assistant.get_capabilities()["capability_count"] == len(
        registry.list_tools()
    )
