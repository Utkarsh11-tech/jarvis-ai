"""
JARVIS Tool Selector Tests

STEP 3B

These tests validate the boundary between the LLM and
the JARVIS Tool Registry.

They do NOT require:
    - Ollama
    - XTTS
    - RTX 5050
    - internet access
    - GUI startup
    - actual tool execution
"""

import pytest

from brain.tools.registry import (
    get_default_registry,
)

from brain.tools.tool_selector import (
    ToolSelection,
    build_tool_selection_prompt,
    parse_tool_selection,
    select_tool,
)

# ==========================================================
# FAKE LLM
# ==========================================================


class FakeLLM:
    """
    Minimal fake LLM used to test the selection boundary.
    """

    def __init__(
        self,
        response,
    ):

        self.response = response
        self.calls = []

    def generate(
        self,
        prompt,
        system_prompt,
        history=None,
    ):

        self.calls.append(
            {
                "prompt": prompt,
                "system_prompt": system_prompt,
                "history": history or [],
            }
        )

        return self.response


# ==========================================================
# TEST 1
# CONVERSATION RESPONSE
# ==========================================================


def test_parse_conversation_response():

    registry = get_default_registry()

    response = """
    {
        "type": "conversation",
        "response": "Artificial intelligence is the simulation of human intelligence by machines."
    }
    """

    result = parse_tool_selection(
        registry,
        response,
    )

    assert isinstance(
        result,
        ToolSelection,
    )

    assert result.kind == ("conversation")

    assert result.response == (
        "Artificial intelligence is the simulation "
        "of human intelligence by machines."
    )

    assert result.tool_name is None
    assert result.arguments is None


# ==========================================================
# TEST 2
# TOOL SELECTION
# ==========================================================


def test_parse_tool_call():

    registry = get_default_registry()

    response = """
    {
        "type": "tool_call",
        "tool": "get_cpu_usage",
        "arguments": {}
    }
    """

    result = parse_tool_selection(
        registry,
        response,
    )

    assert result.kind == "tool"

    assert result.tool_name == ("get_cpu_usage")

    assert result.arguments == {}


# ==========================================================
# TEST 3
# ARGUMENT VALIDATION
# ==========================================================


def test_tool_arguments_are_validated():

    registry = get_default_registry()

    response = """
    {
        "type": "tool_call",
        "tool": "system_command",
        "arguments": {
            "target": "shutdown"
        }
    }
    """

    result = parse_tool_selection(
        registry,
        response,
    )

    assert result.kind == "tool"

    assert result.tool_name == ("system_command")

    assert result.arguments == {"target": "shutdown"}


# ==========================================================
# TEST 4
# CONFIRMATION METADATA REMAINS IN REGISTRY
# ==========================================================


def test_confirmation_metadata_is_not_lost():

    registry = get_default_registry()

    tool = registry.require("system_command")

    assert tool.requires_confirmation is True

    response = """
    {
        "type": "tool_call",
        "tool": "system_command",
        "arguments": {
            "target": "shutdown"
        }
    }
    """

    result = parse_tool_selection(
        registry,
        response,
    )

    assert result.tool_name == ("system_command")


# ==========================================================
# TEST 5
# UNKNOWN TOOL IS REJECTED
# ==========================================================


def test_unknown_tool_is_rejected():

    registry = get_default_registry()

    response = """
    {
        "type": "tool_call",
        "tool": "delete_everything",
        "arguments": {}
    }
    """

    with pytest.raises(
        ValueError,
        match="Unknown JARVIS tool",
    ):

        parse_tool_selection(
            registry,
            response,
        )


# ==========================================================
# TEST 6
# MISSING REQUIRED ARGUMENT
# ==========================================================


def test_missing_required_argument_is_rejected():

    registry = get_default_registry()

    response = """
    {
        "type": "tool_call",
        "tool": "system_command",
        "arguments": {}
    }
    """

    with pytest.raises(
        ValueError,
        match="Missing required argument",
    ):

        parse_tool_selection(
            registry,
            response,
        )


# ==========================================================
# TEST 7
# UNKNOWN ARGUMENT IS REJECTED
# ==========================================================


def test_unknown_argument_is_rejected():

    registry = get_default_registry()

    response = """
    {
        "type": "tool_call",
        "tool": "system_command",
        "arguments": {
            "target": "shutdown",
            "danger": true
        }
    }
    """

    with pytest.raises(
        ValueError,
        match="Unknown argument",
    ):

        parse_tool_selection(
            registry,
            response,
        )


# ==========================================================
# TEST 8
# INVALID ENUM IS REJECTED
# ==========================================================


def test_invalid_enum_value_is_rejected():

    registry = get_default_registry()

    response = """
    {
        "type": "tool_call",
        "tool": "system_command",
        "arguments": {
            "target": "delete"
        }
    }
    """

    with pytest.raises(
        ValueError,
        match="Invalid value",
    ):

        parse_tool_selection(
            registry,
            response,
        )


# ==========================================================
# TEST 9
# MALFORMED JSON IS REJECTED
# ==========================================================


def test_malformed_json_is_rejected():

    registry = get_default_registry()

    response = """
    {
        "type": "tool_call",
        "tool": "get_cpu_usage",
        "arguments":
    """

    with pytest.raises(
        ValueError,
    ):

        parse_tool_selection(
            registry,
            response,
        )


# ==========================================================
# TEST 10
# NON-JSON NATURAL LANGUAGE IS REJECTED
# ==========================================================


def test_natural_language_without_json_is_rejected():

    registry = get_default_registry()

    response = "Sure, I'll check your CPU usage for you."

    with pytest.raises(
        ValueError,
    ):

        parse_tool_selection(
            registry,
            response,
        )


# ==========================================================
# TEST 11
# EMPTY CONVERSATION RESPONSE IS REJECTED
# ==========================================================


def test_empty_conversation_response_is_rejected():

    registry = get_default_registry()

    response = """
    {
        "type": "conversation",
        "response": ""
    }
    """

    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):

        parse_tool_selection(
            registry,
            response,
        )


# ==========================================================
# TEST 12
# INVALID_SELECTION_TYPE_IS_REJECTED
# ==========================================================


def test_invalid_selection_type_is_rejected():

    registry = get_default_registry()

    response = """
    {
        "type": "execute",
        "tool": "get_cpu_usage",
        "arguments": {}
    }
    """

    with pytest.raises(
        ValueError,
        match="Selection type",
    ):

        parse_tool_selection(
            registry,
            response,
        )


# ==========================================================
# TEST 13
# MARKDOWN FENCED JSON IS ACCEPTED
# ==========================================================


def test_markdown_fenced_json_is_accepted():

    registry = get_default_registry()

    response = """
    ```json
    {
        "type": "tool_call",
        "tool": "get_memory_usage",
        "arguments": {}
    }
    ```
    """

    result = parse_tool_selection(
        registry,
        response,
    )

    assert result.kind == "tool"

    assert result.tool_name == ("get_memory_usage")


# ==========================================================
# TEST 14
# LLM IS CALLED WITH CAPABILITY DOCUMENT
# ==========================================================


def test_select_tool_builds_capability_prompt():

    registry = get_default_registry()

    llm = FakeLLM("""
        {
            "type": "tool_call",
            "tool": "get_cpu_usage",
            "arguments": {}
        }
        """)

    result = select_tool(
        llm=llm,
        registry=registry,
        command="What is my CPU usage?",
    )

    assert result.kind == "tool"

    assert result.tool_name == ("get_cpu_usage")

    assert len(llm.calls) == 1

    prompt = llm.calls[0]["prompt"]

    assert "get_cpu_usage" in prompt

    assert "What is my CPU usage?" in prompt


# ==========================================================
# TEST 15
# LLM SYSTEM PROMPT IS PROVIDED
# ==========================================================


def test_selector_provides_system_prompt():

    registry = get_default_registry()

    llm = FakeLLM("""
        {
            "type": "conversation",
            "response": "Hello."
        }
        """)

    select_tool(
        llm=llm,
        registry=registry,
        command="Hello.",
    )

    system_prompt = llm.calls[0]["system_prompt"]

    assert "capability-selection" in system_prompt

    assert "Never invent a capability" in system_prompt


# ==========================================================
# TEST 16
# HISTORY IS FORWARDED
# ==========================================================


def test_selector_forwards_history():

    registry = get_default_registry()

    llm = FakeLLM("""
        {
            "type": "conversation",
            "response": "Your name is Utkarsh."
        }
        """)

    history = [
        {
            "role": "user",
            "content": "My name is Utkarsh.",
        },
        {
            "role": "assistant",
            "content": "I'll remember that.",
        },
    ]

    result = select_tool(
        llm=llm,
        registry=registry,
        command="What is my name?",
        history=history,
    )

    assert result.kind == ("conversation")

    assert llm.calls[0]["history"] == history


# ==========================================================
# TEST 17
# SELECTION DOES NOT EXECUTE TOOL
# ==========================================================


def test_selection_does_not_execute_tool():

    registry = get_default_registry()

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

    llm = FakeLLM("""
        {
            "type": "tool_call",
            "tool": "get_cpu_usage",
            "arguments": {}
        }
        """)

    result = select_tool(
        llm=llm,
        registry=registry,
        command="What's my CPU usage?",
    )

    assert result.tool_name == ("get_cpu_usage")

    assert invoked == []


# ==========================================================
# TEST 18
# NO XTTS DEPENDENCY
# ==========================================================


def test_selector_has_no_voice_dependency():

    import brain.tools.tool_selector as selector

    source_path = selector.__file__

    assert source_path is not None

    with open(
        source_path,
        "r",
        encoding="utf-8",
    ) as file:

        source = file.read().lower()

    # The selector must not import or depend on
    # the voice system.
    assert "voice_manager" not in source
    assert "brain.voices" not in source


# ==========================================================
# TEST 19
# NO EXECUTION IMPORT
# ==========================================================


def test_selector_has_no_executor_dependency():

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


# ==========================================================
# TEST 20
# PROMPT BUILDER DOES NOT EXECUTE
# ==========================================================


def test_prompt_builder_is_read_only():

    registry = get_default_registry()

    prompt = build_tool_selection_prompt(
        registry,
        "What is my memory usage?",
    )

    assert isinstance(
        prompt,
        str,
    )

    assert "get_memory_usage" in prompt

    assert "What is my memory usage?" in prompt


# ==========================================================
# TEST 21
# TOOL SELECTION RESULT IS IMMUTABLE
# ==========================================================


def test_tool_selection_is_immutable():

    result = ToolSelection(
        kind="tool",
        tool_name="get_cpu_usage",
        arguments={},
    )

    with pytest.raises(
        AttributeError,
    ):

        result.kind = "conversation"
