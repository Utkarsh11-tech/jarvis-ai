"""
JARVIS Capability View Tests

Step 2C:

Validate that the Tool Registry can be converted into a clean,
read-only capability representation.

These tests do not require:
    - XTTS
    - Ollama
    - RTX 5050
    - internet access
"""

from brain.tools.capabilities import (
    build_capability_document,
    build_default_capability_document,
    get_capability,
    get_capability_names,
    get_capability_snapshot,
    get_confirmation_required_capabilities,
    get_default_capability_snapshot,
    get_safe_capabilities,
)

from brain.tools.registry import (
    ToolDefinition,
    ToolRegistry,
    get_default_registry,
)

# ==========================================================
# TEST 1
# CAPABILITY SNAPSHOT
# ==========================================================


def test_capability_snapshot_matches_registry():

    registry = get_default_registry()

    snapshot = get_capability_snapshot(registry)

    descriptions = registry.describe()

    assert snapshot == descriptions


# ==========================================================
# TEST 2
# DEFAULT SNAPSHOT
# ==========================================================


def test_default_capability_snapshot():

    snapshot = get_default_capability_snapshot()

    assert isinstance(
        snapshot,
        list,
    )

    assert len(snapshot) == 15


# ==========================================================
# TEST 3
# CAPABILITY NAMES
# ==========================================================


def test_capability_names():

    registry = get_default_registry()

    names = get_capability_names(registry)

    assert names == sorted(names)

    assert "open_application" in names

    assert "get_cpu_usage" in names

    assert "get_memory_usage" in names

    assert "shutdown" not in names


# ==========================================================
# TEST 4
# CAPABILITY LOOKUP
# ==========================================================


def test_capability_lookup():

    registry = get_default_registry()

    capability = get_capability(
        registry,
        "get_cpu_usage",
    )

    assert capability is not None

    assert capability["name"] == ("get_cpu_usage")

    assert capability["requires_confirmation"] is False


# ==========================================================
# TEST 5
# UNKNOWN CAPABILITY
# ==========================================================


def test_unknown_capability_returns_none():

    registry = get_default_registry()

    capability = get_capability(
        registry,
        "does_not_exist",
    )

    assert capability is None


# ==========================================================
# TEST 6
# CONFIRMATION CAPABILITIES
# ==========================================================


def test_confirmation_required_capabilities():

    registry = get_default_registry()

    capabilities = get_confirmation_required_capabilities(registry)

    names = {capability["name"] for capability in capabilities}

    assert names == {
        "system_command",
        "sleep_computer",
    }


# ==========================================================
# TEST 7
# SAFE CAPABILITIES
# ==========================================================


def test_safe_capabilities():

    registry = get_default_registry()

    safe = get_safe_capabilities(registry)

    names = {capability["name"] for capability in safe}

    assert "get_system_info" in names

    assert "get_cpu_usage" in names

    assert "get_memory_usage" in names

    assert "system_command" not in names

    assert "sleep_computer" not in names


# ==========================================================
# TEST 8
# CAPABILITY DOCUMENT
# ==========================================================


def test_capability_document():

    registry = get_default_registry()

    document = build_capability_document(registry)

    assert isinstance(
        document,
        dict,
    )

    assert document["name"] == ("JARVIS")

    assert document["capability_count"] == 15

    assert isinstance(
        document["capabilities"],
        list,
    )

    assert len(document["capabilities"]) == 15


# ==========================================================
# TEST 9
# DEFAULT CAPABILITY DOCUMENT
# ==========================================================


def test_default_capability_document():

    document = build_default_capability_document()

    assert document["name"] == ("JARVIS")

    assert document["capability_count"] == 15


# ==========================================================
# TEST 10
# HANDLERS ARE NOT EXPOSED
# ==========================================================


def test_handlers_are_not_exposed():

    registry = get_default_registry()

    snapshot = get_capability_snapshot(registry)

    for capability in snapshot:

        assert "handler" not in (capability)


# ==========================================================
# TEST 11
# CAPABILITY SCHEMAS ARE PRESERVED
# ==========================================================


def test_capability_schemas_are_preserved():

    registry = get_default_registry()

    capability = get_capability(
        registry,
        "get_disk_usage",
    )

    assert capability is not None

    schema = capability["input_schema"]

    assert schema["type"] == ("object")

    assert "properties" in schema


# ==========================================================
# TEST 12
# SYSTEM COMMAND METADATA
# ==========================================================


def test_system_command_metadata():

    registry = get_default_registry()

    capability = get_capability(
        registry,
        "system_command",
    )

    assert capability is not None

    assert capability["requires_confirmation"] is True

    assert capability["input_schema"]["properties"]["target"]["enum"] == [
        "shutdown",
        "restart",
    ]


# ==========================================================
# TEST 13
# CAPABILITY COUNT MATCHES REGISTRY
# ==========================================================


def test_capability_count_matches_registry():

    registry = get_default_registry()

    snapshot = get_capability_snapshot(registry)

    assert len(snapshot) == len(registry.list_tools())


# ==========================================================
# TEST 14
# INVALID REGISTRY TYPE
# ==========================================================


def test_invalid_registry_type_is_rejected():

    try:

        get_capability_snapshot(None)

    except TypeError as error:

        assert "ToolRegistry" in str(error)

    else:

        raise AssertionError("Invalid registry was accepted.")


# ==========================================================
# TEST 15
# INVALID CAPABILITY NAME
# ==========================================================


def test_invalid_capability_name_is_rejected():

    registry = get_default_registry()

    try:

        get_capability(
            registry,
            "",
        )

    except ValueError as error:

        assert "cannot be empty" in str(error)

    else:

        raise AssertionError("Empty capability name was accepted.")


# ==========================================================
# TEST 16
# CAPABILITY DOCUMENT IS LLM SAFE
# ==========================================================


def test_capability_document_is_llm_safe():

    registry = get_default_registry()

    document = build_capability_document(registry)

    for capability in document["capabilities"]:

        assert set(capability.keys()) == {
            "name",
            "description",
            "input_schema",
            "requires_confirmation",
        }

        assert callable(registry.require(capability["name"]).handler)


# ==========================================================
# TEST 17
# REGISTRY REMAINS EXECUTABLE
# ==========================================================


def test_capability_view_does_not_disable_registry():

    registry = get_default_registry()

    # Build the capability view first.
    build_capability_document(registry)

    # Then prove the original registry still works.
    result = registry.invoke("get_system_info")

    assert isinstance(
        result,
        dict,
    )

    assert "system" in result
