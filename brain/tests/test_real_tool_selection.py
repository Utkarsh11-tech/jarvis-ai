"""
JARVIS Real Qwen Tool Selection Tests

STEP 3C

These tests connect the existing Tool Selector to the
real local Ollama/Qwen runtime.

They verify that Qwen can select registered JARVIS
capabilities without actually executing them.

Requires:
    - Ollama running
    - configured Qwen model available

Does NOT require:
    - XTTS
    - RTX 5050
    - GUI
    - actual tool execution
    - internet access
"""

import json

import pytest

from brain.models.ollama_client import (
    OllamaClient,
)

from brain.tools.registry import (
    get_default_registry,
)

from brain.tools.tool_selector import (
    TOOL_SELECTOR_SYSTEM_PROMPT,
    ToolSelection,
    select_tool,
)

# ==========================================================
# CONFIGURATION
# ==========================================================


EXPECTED_MODEL = "qwen3:8b"


# ==========================================================
# FIXTURES
# ==========================================================


@pytest.fixture(scope="module")
def ollama():
    """
    Create the real Ollama client.

    Skip the suite cleanly if Ollama or the configured
    model is unavailable.
    """

    client = OllamaClient()

    if not client.is_available():

        pytest.skip("Ollama server is not available.")

    if not client.has_model():

        pytest.skip(f"Ollama model '{client.get_model()}' " "is not available.")

    return client


@pytest.fixture(scope="module")
def registry():
    """
    Return the real default JARVIS registry.
    """

    return get_default_registry()


# ==========================================================
# TEST 1
# OLLAMA CONNECTION
# ==========================================================


def test_real_ollama_connection(
    ollama,
):

    assert ollama.is_available() is True


# ==========================================================
# TEST 2
# QWEN MODEL
# ==========================================================


def test_real_qwen_model_available(
    ollama,
):

    assert ollama.has_model() is True

    print(f"\nQwen model: {ollama.get_model()}")

    assert ollama.get_model() == EXPECTED_MODEL


# ==========================================================
# TEST 3
# TOOL SELECTION PROMPT
# ==========================================================


def test_selector_uses_real_capability_document(
    ollama,
    registry,
):

    result = select_tool(
        llm=ollama,
        registry=registry,
        command=("What is my CPU usage?"),
    )

    assert isinstance(
        result,
        ToolSelection,
    )

    assert result.kind in {
        "tool",
        "conversation",
    }


# ==========================================================
# TEST 4
# CPU REQUEST
# ==========================================================


def test_real_qwen_selects_cpu_capability(
    ollama,
    registry,
):

    result = select_tool(
        llm=ollama,
        registry=registry,
        command=("What is my CPU usage?"),
    )

    print(f"\nCPU selection: {result}")

    assert result.kind == "tool"

    assert result.tool_name == ("get_cpu_usage")

    assert result.arguments == {}


# ==========================================================
# TEST 5
# MEMORY REQUEST
# ==========================================================


def test_real_qwen_selects_memory_capability(
    ollama,
    registry,
):

    result = select_tool(
        llm=ollama,
        registry=registry,
        command=("How much RAM am I using?"),
    )

    print(f"\nMemory selection: {result}")

    assert result.kind == "tool"

    assert result.tool_name == ("get_memory_usage")

    assert result.arguments == {}


# ==========================================================
# TEST 6
# DISK REQUEST
# ==========================================================


def test_real_qwen_selects_disk_capability(
    ollama,
    registry,
):

    result = select_tool(
        llm=ollama,
        registry=registry,
        command=("How much disk space do I have?"),
    )

    print(f"\nDisk selection: {result}")

    assert result.kind == "tool"

    assert result.tool_name == ("get_disk_usage")

    assert isinstance(
        result.arguments,
        dict,
    )


# ==========================================================
# TEST 7
# SYSTEM INFORMATION
# ==========================================================


def test_real_qwen_selects_system_info(
    ollama,
    registry,
):

    result = select_tool(
        llm=ollama,
        registry=registry,
        command=("Tell me information about " "this computer."),
    )

    print(f"\nSystem info selection: {result}")

    assert result.kind == "tool"

    assert result.tool_name == ("get_system_info")

    assert result.arguments == {}


# ==========================================================
# TEST 8
# SHUTDOWN REQUEST
# ==========================================================


def test_real_qwen_selects_shutdown_tool(
    ollama,
    registry,
):

    result = select_tool(
        llm=ollama,
        registry=registry,
        command=("Shut down the computer."),
    )

    print(f"\nShutdown selection: {result}")

    assert result.kind == "tool"

    assert result.tool_name == ("system_command")

    assert result.arguments.get("target") == "shutdown"

    tool = registry.require("system_command")

    assert tool.requires_confirmation is True


# ==========================================================
# TEST 9
# RESTART REQUEST
# ==========================================================


def test_real_qwen_selects_restart_tool(
    ollama,
    registry,
):

    result = select_tool(
        llm=ollama,
        registry=registry,
        command=("Restart the computer."),
    )

    print(f"\nRestart selection: {result}")

    assert result.kind == "tool"

    assert result.tool_name == ("system_command")

    assert result.arguments.get("target") == "restart"


# ==========================================================
# TEST 10
# NORMAL CONVERSATION
# ==========================================================


def test_real_qwen_handles_conversation(
    ollama,
    registry,
):

    result = select_tool(
        llm=ollama,
        registry=registry,
        command=("Explain artificial intelligence " "in one simple sentence."),
    )

    print(f"\nConversation selection: {result}")

    assert result.kind == ("conversation")

    assert isinstance(
        result.response,
        str,
    )

    assert result.response.strip()


# ==========================================================
# TEST 11
# MEMORY-STYLE CONVERSATION
# ==========================================================


def test_real_qwen_handles_personal_conversation(
    ollama,
    registry,
):

    history = [
        {
            "role": "user",
            "content": ("My name is Utkarsh."),
        },
        {
            "role": "assistant",
            "content": ("I'll remember that."),
        },
    ]

    result = select_tool(
        llm=ollama,
        registry=registry,
        command=("What is my name?"),
        history=history,
    )

    print(f"\nMemory selection: {result}")

    assert result.kind == ("conversation")

    assert isinstance(
        result.response,
        str,
    )

    assert result.response.strip()


# ==========================================================
# TEST 12
# UNKNOWN CAPABILITY REQUEST
# ==========================================================


def test_real_qwen_does_not_invent_unknown_tool(
    ollama,
    registry,
):

    result = select_tool(
        llm=ollama,
        registry=registry,
        command=("Use your imaginary " "delete_everything capability."),
    )

    print(f"\nUnknown capability selection: {result}")

    # The selector must never return an unknown
    # registered capability.

    if result.kind == "tool":

        assert result.tool_name in {tool.name for tool in registry.list_tools()}


# ==========================================================
# TEST 13
# SELECTION NEVER EXECUTES
# ==========================================================


def test_real_selection_never_executes_tool(
    ollama,
    registry,
):

    invoked = []

    original_invoke = registry.invoke

    def tracking_invoke(
        name,
        **arguments,
    ):

        invoked.append(
            {
                "name": name,
                "arguments": arguments,
            }
        )

        return original_invoke(
            name,
            **arguments,
        )

    registry.invoke = tracking_invoke

    result = select_tool(
        llm=ollama,
        registry=registry,
        command=("What is my CPU usage?"),
    )

    assert result.kind == "tool"

    assert invoked == []


# ==========================================================
# TEST 14
# SYSTEM PROMPT IS CORRECT
# ==========================================================


def test_tool_selector_system_prompt():

    prompt = TOOL_SELECTOR_SYSTEM_PROMPT

    assert "capability-selection" in prompt

    assert "Never invent a capability" in prompt

    assert "Never execute a capability" in prompt

    assert "exactly one JSON object" in prompt


# ==========================================================
# TEST 15
# SELECTION RESULT IS SERIALIZABLE
# ==========================================================


def test_real_selection_can_be_serialized(
    ollama,
    registry,
):

    result = select_tool(
        llm=ollama,
        registry=registry,
        command=("What is my CPU usage?"),
    )

    payload = {
        "kind": result.kind,
        "tool_name": result.tool_name,
        "arguments": result.arguments,
        "response": result.response,
    }

    encoded = json.dumps(
        payload,
        ensure_ascii=False,
    )

    decoded = json.loads(encoded)

    assert decoded["kind"] == (result.kind)


# ==========================================================
# TEST 16
# REAL QWEN SELECTION USES REGISTERED TOOL NAMES
# ==========================================================


def test_real_qwen_tool_is_registered(
    ollama,
    registry,
):

    result = select_tool(
        llm=ollama,
        registry=registry,
        command=("Tell me my current system information."),
    )

    if result.kind == "tool":

        registered_names = {tool.name for tool in registry.list_tools()}

        assert result.tool_name in registered_names


# ==========================================================
# TEST 17
# TOOL SELECTION DOES NOT REQUIRE XTTS
# ==========================================================


def test_real_tool_selection_has_no_voice_dependency():

    import brain.tools.tool_selector as selector

    source_path = selector.__file__

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
# TOOL SELECTION DOES NOT IMPORT EXECUTOR
# ==========================================================


def test_real_tool_selection_has_no_executor_dependency():

    import brain.tools.tool_selector as selector

    source_path = selector.__file__

    assert source_path is not None

    with open(
        source_path,
        "r",
        encoding="utf-8",
    ) as file:

        source = file.read().lower()

    assert "brain.core.executor" not in source
