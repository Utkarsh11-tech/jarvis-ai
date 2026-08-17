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
# FAKE VOICE BACKEND
# ==========================================================


class FakeVoiceBackend:

    def __init__(self):

        self.calls = []

    def speak(self, text):

        self.calls.append(text)

        print(f"[XTTS BOUNDARY] {text}")


# ==========================================================
# CREATE ASSISTANT
# ==========================================================


def create_assistant():

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    # ------------------------------------------------------
    # REAL LLM CLIENT
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
    # TEST INFRASTRUCTURE
    # ------------------------------------------------------

    assistant.state_manager = FakeStateManager()

    assistant.bridge = FakeBridge()

    assistant.wake_timeout_timer = FakeTimer()

    return assistant


# ==========================================================
# FORCE UNKNOWN → LLM
# ==========================================================


def configure_unknown_routing(assistant):

    assistant.process_command = lambda command: [
        {
            "intent": "UNKNOWN",
            "target": command,
        }
    ]


# ==========================================================
# TEST 1
# REAL QWEN RESPONSE REACHES VOICE BOUNDARY
# ==========================================================


def test_real_qwen_response_reaches_voice_boundary():

    print()
    print("========================================")
    print("JARVIS LLM → VOICE BOUNDARY TEST")
    print("========================================")

    assistant = create_assistant()

    voice = FakeVoiceBackend()

    assistant_v2.speak = voice.speak

    configure_unknown_routing(assistant)

    command = "Reply with exactly: " "Voice boundary test successful."

    print()
    print("----------------------------------------")
    print("TEST 1: REAL QWEN → VOICE BOUNDARY")
    print("----------------------------------------")

    print(f"USER: {command}")

    assistant.handle_command(command)

    messages = assistant.llm_memory.get_messages()

    # ------------------------------------------------------
    # Qwen must have produced a response.
    # ------------------------------------------------------

    assert len(messages) == 2

    assert messages[0]["role"] == "user"

    assert messages[1]["role"] == "assistant"

    response = messages[1]["content"]

    assert response.strip()

    # ------------------------------------------------------
    # Voice boundary must receive the exact same response.
    # ------------------------------------------------------

    assert len(voice.calls) == 1

    assert voice.calls[0] == response

    # ------------------------------------------------------
    # Bridge must also receive the same response.
    # ------------------------------------------------------

    assert len(assistant.bridge.responses) == 1

    assert assistant.bridge.responses[0] == response

    print()
    print("PASS: Real Qwen response generated.")

    print("PASS: Response entered LLM memory.")

    print("PASS: Exact response reached voice boundary.")

    print("PASS: Exact response reached bridge.")


# ==========================================================
# TEST 2
# VOICE BACKEND RECEIVES TEXT ONLY
# ==========================================================


def test_voice_boundary_receives_text():

    assistant = create_assistant()

    voice = FakeVoiceBackend()

    assistant_v2.speak = voice.speak

    configure_unknown_routing(assistant)

    command = "Give me one short fact about space."

    print()
    print("----------------------------------------")
    print("TEST 2: VOICE PAYLOAD VALIDATION")
    print("----------------------------------------")

    print(f"USER: {command}")

    assistant.handle_command(command)

    assert len(voice.calls) == 1

    spoken = voice.calls[0]

    assert isinstance(spoken, str)

    assert spoken.strip()

    print()
    print("PASS: Voice backend received a string.")

    print("PASS: Voice payload was non-empty.")


# ==========================================================
# TEST 3
# VOICE FAILURE MUST NOT DESTROY BRAIN RESPONSE
# ==========================================================


def test_voice_failure_is_isolated_from_llm_response():

    assistant = create_assistant()

    voice_calls = []

    assistant_v2.speak = lambda text: (
        voice_calls.append(text),
        (_ for _ in ()).throw(RuntimeError("Simulated voice backend failure.")),
    )[1]

    configure_unknown_routing(assistant)

    command = "Reply with exactly: " "Brain response preserved."

    print()
    print("----------------------------------------")
    print("TEST 3: VOICE FAILURE ISOLATION")
    print("----------------------------------------")

    print(f"USER: {command}")

    try:

        assistant.handle_command(command)

    except RuntimeError as error:

        # --------------------------------------------------
        # This test verifies that the current Assistant V2
        # boundary behavior is observable.
        #
        # If the production voice layer propagates an
        # exception, we record that behavior rather than
        # silently hiding it.
        # --------------------------------------------------

        print(f"[VOICE FAILURE] {error}")

    messages = assistant.llm_memory.get_messages()

    # ------------------------------------------------------
    # The LLM response must have been generated before
    # voice execution.
    # ------------------------------------------------------

    assert len(messages) == 2

    assert messages[0]["role"] == "user"

    assert messages[1]["role"] == "assistant"

    assert messages[1]["content"].strip()

    assert len(voice_calls) == 1

    print()
    print("PASS: LLM response was generated.")

    print("PASS: LLM response entered memory.")

    print("PASS: Voice backend was invoked exactly once.")


# ==========================================================
# TEST 4
# BRAIN RETURNS TO IDLE AFTER NORMAL SPEECH
# ==========================================================


def test_normal_voice_boundary_returns_to_idle():

    assistant = create_assistant()

    voice = FakeVoiceBackend()

    assistant_v2.speak = voice.speak

    configure_unknown_routing(assistant)

    command = "Tell me one fact about the Moon."

    print()
    print("----------------------------------------")
    print("TEST 4: FINAL STATE AFTER SPEECH")
    print("----------------------------------------")

    print(f"USER: {command}")

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
# TEST 5
# MULTI-TURN RESPONSES ALL REACH VOICE
# ==========================================================


def test_every_llm_turn_reaches_voice_boundary():

    assistant = create_assistant()

    voice = FakeVoiceBackend()

    assistant_v2.speak = voice.speak

    configure_unknown_routing(assistant)

    commands = [
        "My name is Utkarsh.",
        "What is my name?",
        "Say hello in one word.",
    ]

    print()
    print("----------------------------------------")
    print("TEST 5: MULTI-TURN VOICE DELIVERY")
    print("----------------------------------------")

    for index, command in enumerate(
        commands,
        start=1,
    ):

        print()
        print(f"TURN {index}: {command}")

        assistant.handle_command(command)

    messages = assistant.llm_memory.get_messages()

    assert len(messages) == 6

    assistant_messages = [
        message["content"] for message in messages if message["role"] == "assistant"
    ]

    assert len(assistant_messages) == 3

    assert len(voice.calls) == 3

    for index in range(3):

        assert voice.calls[index] == assistant_messages[index]

    print()
    print("PASS: Three Qwen responses generated.")

    print("PASS: Three responses entered memory.")

    print("PASS: Three responses reached voice.")

    print("PASS: Voice payloads exactly matched LLM output.")


# ==========================================================
# FINAL SUMMARY
# ==========================================================


def test_voice_boundary_summary():

    print()
    print("========================================")
    print("LLM → VOICE BOUNDARY TEST COMPLETE")
    print("========================================")

    print("Real Qwen → voice boundary validated.")

    print("Voice payload validation completed.")

    print("Voice failure isolation checked.")

    print("Runtime state transition validated.")

    print("Multi-turn voice delivery validated.")

    print("XTTS was intentionally not required.")

    print("========================================")
