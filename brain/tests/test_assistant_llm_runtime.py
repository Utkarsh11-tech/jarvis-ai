from brain.core import assistant_v2
from brain.core.context import ContextManager
from brain.core.conversation_manager import ConversationManager
from brain.core.state import JarvisState
from brain.memory.conversation_memory import ConversationMemory
from brain.models.ollama_client import OllamaClient

# ==========================================================
# FAKE TIMER
# ==========================================================


class FakeTimer:

    def isActive(self):
        return False

    def stop(self):
        pass

    def start(self, milliseconds):
        pass


# ==========================================================
# FAKE STATE MANAGER
# ==========================================================


class FakeStateManager:

    def __init__(self):

        self.current_state = JarvisState.IDLE
        self.states = []

    def set_state(self, state):

        self.current_state = state
        self.states.append(state)

        print(f"[STATE] {state}")

    def get_state(self):

        return self.current_state


# ==========================================================
# FAKE BRIDGE
# ==========================================================


class FakeBridge:

    def __init__(self):

        self.responses = []

    def send_response(self, response):

        self.responses.append(response)

        print(f"[BRIDGE] {response}")


# ==========================================================
# FAKE VOICE
# ==========================================================


class FakeVoice:

    def __init__(self):

        self.responses = []

    def speak(self, text):

        self.responses.append(text)

        print(f"[VOICE] {text}")


# ==========================================================
# CREATE REAL ASSISTANT V2
# ==========================================================


def create_assistant():
    """
    Creates the real Assistant V2 class without launching
    the GUI or requiring XTTS.

    The production LLM path remains completely real.
    """

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    # ------------------------------------------------------
    # REAL OLLAMA CLIENT
    # ------------------------------------------------------

    assistant.ollama = OllamaClient()

    # ------------------------------------------------------
    # REAL LLM MEMORY
    # ------------------------------------------------------

    assistant.llm_memory = ConversationMemory(max_messages=20)

    # ------------------------------------------------------
    # REAL CONVERSATION MANAGER
    # ------------------------------------------------------

    assistant.conversation = ConversationManager()

    # ------------------------------------------------------
    # REAL CONTEXT MANAGER
    # ------------------------------------------------------

    assistant.context = ContextManager()

    # ------------------------------------------------------
    # TEST STATE MANAGER
    # ------------------------------------------------------

    assistant.state_manager = FakeStateManager()

    # ------------------------------------------------------
    # TEST BRIDGE
    # ------------------------------------------------------

    assistant.bridge = FakeBridge()

    # ------------------------------------------------------
    # TEST TIMER
    # ------------------------------------------------------

    assistant.wake_timeout_timer = FakeTimer()

    return assistant


# ==========================================================
# TEST 1
# REAL CONVERSATION → QWEN
# ==========================================================


def test_real_assistant_conversation():

    print()
    print("========================================")
    print("JARVIS ASSISTANT LLM RUNTIME TEST")
    print("========================================")

    voice = FakeVoice()

    assistant_v2.speak = voice.speak

    assistant = create_assistant()

    command = "Explain artificial intelligence " "in one simple sentence."

    print()
    print("----------------------------------------")
    print("TEST 1: REAL CONVERSATION → QWEN")
    print("----------------------------------------")

    print(f"USER: {command}")

    result = assistant.handle_command(command)

    assert result is None

    assert len(assistant.llm_memory.get_messages()) == 2

    messages = assistant.llm_memory.get_messages()

    assert messages[0]["role"] == "user"

    assert messages[1]["role"] == "assistant"

    assert messages[0]["content"] == command

    assert messages[1]["content"]

    assert len(voice.responses) == 1

    assert voice.responses[0] == messages[1]["content"]

    assert assistant.state_manager.get_state() == JarvisState.IDLE

    print()
    print("PASS: Assistant V2 reached real Qwen.")

    print("PASS: Qwen response entered memory.")

    print("PASS: Qwen response reached voice boundary.")

    print("PASS: Assistant returned to IDLE.")


# ==========================================================
# TEST 2
# MEMORY STORAGE + RECALL
# ==========================================================


def test_real_assistant_memory_recall():

    voice = FakeVoice()

    assistant_v2.speak = voice.speak

    assistant = create_assistant()

    print()
    print("----------------------------------------")
    print("TEST 2: REAL MEMORY STORAGE + RECALL")
    print("----------------------------------------")

    first_command = "My name is Utkarsh. " "Remember that."

    print(f"USER: {first_command}")

    assistant.handle_command(first_command)

    messages_after_first = assistant.llm_memory.get_messages()

    assert len(messages_after_first) == 2

    second_command = "What is my name?"

    print()
    print(f"USER: {second_command}")

    assistant.handle_command(second_command)

    messages = assistant.llm_memory.get_messages()

    assert len(messages) == 4

    assert messages[0]["role"] == "user"

    assert messages[1]["role"] == "assistant"

    assert messages[2]["role"] == "user"

    assert messages[3]["role"] == "assistant"

    response = messages[3]["content"]

    assert response

    assert "utkarsh" in response.lower()

    print()
    print("PASS: First message stored.")

    print("PASS: Second message received.")

    print("PASS: Qwen recalled Utkarsh.")

    print("PASS: Four conversation messages stored.")


# ==========================================================
# TEST 3
# MULTI-TURN CONTINUATION
# ==========================================================


def test_real_assistant_multiturn_conversation():

    voice = FakeVoice()

    assistant_v2.speak = voice.speak

    assistant = create_assistant()

    print()
    print("----------------------------------------")
    print("TEST 3: MULTI-TURN CONVERSATION")
    print("----------------------------------------")

    commands = [
        "I am building a project called JARVIS.",
        "What project am I building?",
        "What is the main purpose of this project?",
    ]

    for index, command in enumerate(
        commands,
        start=1,
    ):

        print()
        print(f"TURN {index}")

        print(f"USER: {command}")

        assistant.handle_command(command)

    messages = assistant.llm_memory.get_messages()

    assert len(messages) == 6

    roles = [message["role"] for message in messages]

    expected_roles = [
        "user",
        "assistant",
        "user",
        "assistant",
        "user",
        "assistant",
    ]

    assert roles == expected_roles

    responses = [
        message["content"] for message in messages if message["role"] == "assistant"
    ]

    assert len(responses) == 3

    assert all(response.strip() for response in responses)

    print()
    print("PASS: Three real conversation turns completed.")

    print("PASS: Six messages stored.")

    print("PASS: Conversation roles are correct.")


# ==========================================================
# TEST 4
# UNKNOWN ROUTING
# ==========================================================


def test_unknown_input_uses_llm_path():

    voice = FakeVoice()

    assistant_v2.speak = voice.speak

    assistant = create_assistant()

    command = "Why is the sky blue?"

    print()
    print("----------------------------------------")
    print("TEST 4: UNKNOWN → REAL LLM PATH")
    print("----------------------------------------")

    print(f"USER: {command}")

    assistant.handle_command(command)

    messages = assistant.llm_memory.get_messages()

    assert len(messages) == 2

    assert messages[0]["content"] == command

    assert messages[1]["role"] == "assistant"

    assert messages[1]["content"]

    assert len(voice.responses) == 1

    print()
    print("PASS: UNKNOWN input reached Qwen.")

    print("PASS: Qwen response returned.")

    print("PASS: Response crossed voice boundary.")


# ==========================================================
# TEST 5
# FINAL RUNTIME STATE
# ==========================================================


def test_assistant_runtime_state():

    voice = FakeVoice()

    assistant_v2.speak = voice.speak

    assistant = create_assistant()

    command = "Give me one short fact about space."

    print()
    print("----------------------------------------")
    print("TEST 5: FINAL RUNTIME STATE")
    print("----------------------------------------")

    assistant.handle_command(command)

    states = assistant.state_manager.states

    assert JarvisState.THINKING in states

    assert JarvisState.SPEAKING in states

    assert states[-1] == JarvisState.IDLE

    print()
    print("PASS: THINKING state reached.")

    print("PASS: SPEAKING state reached.")

    print("PASS: JARVIS returned to IDLE.")


# ==========================================================
# FINAL SUMMARY
# ==========================================================


def test_runtime_summary():

    print()
    print("========================================")
    print("ASSISTANT V2 LLM RUNTIME TEST COMPLETE")
    print("========================================")

    print("Real Assistant V2 → Qwen path validated.")

    print("XTTS was intentionally not required.")

    print("========================================")
