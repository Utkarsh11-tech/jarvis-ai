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
# CREATE TEST ASSISTANT
# ==========================================================


def create_assistant():

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    # ------------------------------------------------------
    # Real Ollama client
    # ------------------------------------------------------

    assistant.ollama = OllamaClient()

    # ------------------------------------------------------
    # Real conversation memory
    # ------------------------------------------------------

    assistant.llm_memory = ConversationMemory(max_messages=20)

    # ------------------------------------------------------
    # Real conversation manager
    # ------------------------------------------------------

    assistant.conversation = ConversationManager()

    # ------------------------------------------------------
    # Real context manager
    # ------------------------------------------------------

    assistant.context = ContextManager()

    # ------------------------------------------------------
    # Test infrastructure
    # ------------------------------------------------------

    assistant.state_manager = FakeStateManager()

    assistant.bridge = FakeBridge()

    assistant.wake_timeout_timer = FakeTimer()

    return assistant


# ==========================================================
# FORCE UNKNOWN ROUTING
# ==========================================================


def configure_unknown_routing(assistant):
    """
    Forces the command through the production UNKNOWN
    → Qwen routing path without depending on the parser.
    """

    assistant.process_command = lambda command: [
        {
            "intent": "UNKNOWN",
            "target": command,
        }
    ]


# ==========================================================
# TEST 1
# OLLAMA FAILURE IS HANDLED
# ==========================================================


def test_ollama_failure_is_handled():

    print()
    print("========================================")
    print("JARVIS LLM FAILURE BOUNDARY TEST")
    print("========================================")

    print()
    print("----------------------------------------")
    print("TEST 1: OLLAMA FAILURE HANDLING")
    print("----------------------------------------")

    assistant = create_assistant()

    voice = FakeVoice()

    assistant_v2.speak = voice.speak

    configure_unknown_routing(assistant)

    # ------------------------------------------------------
    # Simulate Ollama being unavailable.
    # ------------------------------------------------------

    def failing_generate(**kwargs):

        raise RuntimeError("Simulated Ollama connection failure.")

    assistant.ollama.generate = failing_generate

    command = "Explain quantum computing."

    print(f"USER: {command}")

    assistant.handle_command(command)

    # ------------------------------------------------------
    # Validate fallback response.
    # ------------------------------------------------------

    expected_response = "I'm unable to reach my language " "model right now."

    assert len(assistant.bridge.responses) == 1

    assert assistant.bridge.responses[0] == expected_response

    assert len(voice.responses) == 1

    assert voice.responses[0] == expected_response

    # ------------------------------------------------------
    # Validate runtime state.
    # ------------------------------------------------------

    assert assistant.state_manager.get_state() == JarvisState.IDLE

    print()
    print("PASS: Ollama failure was detected.")

    print("PASS: Fallback response was generated.")

    print("PASS: Fallback reached voice boundary.")

    print("PASS: Fallback reached bridge.")

    print("PASS: JARVIS returned to IDLE.")


# ==========================================================
# TEST 2
# FAILED REQUEST DOES NOT ENTER MEMORY
# ==========================================================


def test_failed_llm_request_does_not_pollute_memory():

    print()
    print("----------------------------------------")
    print("TEST 2: FAILED REQUEST MEMORY SAFETY")
    print("----------------------------------------")

    assistant = create_assistant()

    voice = FakeVoice()

    assistant_v2.speak = voice.speak

    configure_unknown_routing(assistant)

    def failing_generate(**kwargs):

        raise RuntimeError("Simulated Ollama failure.")

    assistant.ollama.generate = failing_generate

    command = "Tell me something interesting."

    assistant.handle_command(command)

    messages = assistant.llm_memory.get_messages()

    # ------------------------------------------------------
    # Production code adds messages only after a
    # successful Qwen response.
    # ------------------------------------------------------

    assert len(messages) == 0

    print()
    print("PASS: Failed LLM request was not stored.")

    print("PASS: Conversation memory remained clean.")


# ==========================================================
# TEST 3
# JARVIS RECOVERS AFTER LLM FAILURE
# ==========================================================


def test_assistant_recovers_after_llm_failure():

    print()
    print("----------------------------------------")
    print("TEST 3: RECOVERY AFTER LLM FAILURE")
    print("----------------------------------------")

    assistant = create_assistant()

    voice = FakeVoice()

    assistant_v2.speak = voice.speak

    configure_unknown_routing(assistant)

    # ------------------------------------------------------
    # First request fails.
    # ------------------------------------------------------

    def failing_generate(**kwargs):

        raise RuntimeError("Simulated temporary failure.")

    assistant.ollama.generate = failing_generate

    failed_command = "What is artificial intelligence?"

    print(f"FIRST USER: {failed_command}")

    assistant.handle_command(failed_command)

    assert assistant.state_manager.get_state() == JarvisState.IDLE

    # ------------------------------------------------------
    # Now restore the real Ollama generate method.
    # ------------------------------------------------------

    real_client = OllamaClient()

    assistant.ollama = real_client

    successful_command = "Reply with exactly: Recovery successful."

    print()
    print(f"SECOND USER: {successful_command}")

    assistant.handle_command(successful_command)

    messages = assistant.llm_memory.get_messages()

    # ------------------------------------------------------
    # The successful request should now be stored.
    # ------------------------------------------------------

    assert len(messages) == 2

    assert messages[0]["role"] == "user"

    assert messages[1]["role"] == "assistant"

    assert messages[1]["content"]

    assert assistant.state_manager.get_state() == JarvisState.IDLE

    print()
    print("PASS: JARVIS survived the failed request.")

    print("PASS: Ollama client recovered.")

    print("PASS: A later real request succeeded.")

    print("PASS: Successful response entered memory.")

    print("PASS: JARVIS returned to IDLE.")


# ==========================================================
# TEST 4
# EMPTY LLM RESPONSE IS HANDLED
# ==========================================================


def test_empty_llm_response_is_handled():

    print()
    print("----------------------------------------")
    print("TEST 4: EMPTY QWEN RESPONSE")
    print("----------------------------------------")

    assistant = create_assistant()

    voice = FakeVoice()

    assistant_v2.speak = voice.speak

    configure_unknown_routing(assistant)

    # ------------------------------------------------------
    # Simulate Qwen returning nothing.
    # ------------------------------------------------------

    def empty_generate(**kwargs):

        return ""

    assistant.ollama.generate = empty_generate

    command = "Give me a short answer."

    print(f"USER: {command}")

    assistant.handle_command(command)

    expected_response = "I didn't receive a response " "from the language model."

    assert len(assistant.bridge.responses) == 1

    assert assistant.bridge.responses[0] == expected_response

    assert len(voice.responses) == 1

    assert voice.responses[0] == expected_response

    assert assistant.state_manager.get_state() == JarvisState.IDLE

    assert len(assistant.llm_memory.get_messages()) == 0

    print()
    print("PASS: Empty Qwen response was detected.")

    print("PASS: Fallback response was generated.")

    print("PASS: Empty response did not enter memory.")

    print("PASS: JARVIS returned to IDLE.")


# ==========================================================
# TEST 5
# FINAL STATE VALIDATION
# ==========================================================


def test_failure_boundary_state_sequence():

    print()
    print("----------------------------------------")
    print("TEST 5: FAILURE STATE SEQUENCE")
    print("----------------------------------------")

    assistant = create_assistant()

    voice = FakeVoice()

    assistant_v2.speak = voice.speak

    configure_unknown_routing(assistant)

    def failing_generate(**kwargs):

        raise RuntimeError("Simulated failure.")

    assistant.ollama.generate = failing_generate

    assistant.handle_command("Test failure handling.")

    states = assistant.state_manager.states

    assert JarvisState.THINKING in states

    assert JarvisState.SPEAKING in states

    assert states[-1] == JarvisState.IDLE

    print()
    print("PASS: THINKING state reached.")

    print("PASS: SPEAKING state reached.")

    print("PASS: Failure path ended in IDLE.")


# ==========================================================
# FINAL SUMMARY
# ==========================================================


def test_failure_boundary_summary():

    print()
    print("========================================")
    print("LLM FAILURE BOUNDARY TEST COMPLETE")
    print("========================================")

    print("Ollama failure handling validated.")

    print("Memory safety validated.")

    print("Recovery path validated.")

    print("Empty-response handling validated.")

    print("XTTS was intentionally not required.")

    print("========================================")
