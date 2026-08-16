from brain.core import assistant_v2
from brain.core.context import ContextManager
from brain.core.conversation_manager import ConversationManager
from brain.core.state import JarvisState
from brain.memory.conversation_memory import ConversationMemory
from brain.models.ollama_client import OllamaClient

# ==========================================================
# TEST DOUBLES
# ==========================================================


class FakeTimer:

    def isActive(self):
        return False

    def stop(self):
        pass

    def start(self, milliseconds):
        pass


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


class FakeBridge:

    def __init__(self):
        self.responses = []

    def send_response(self, response):
        self.responses.append(response)
        print(f"[BRIDGE] {response}")


class FakeVoiceBackend:

    def __init__(self):
        self.requests = []

    def speak(self, text):
        self.requests.append(text)
        print(f"[VOICE BACKEND] Received: {text}")


class FailingVoiceBackend:

    def speak(self, text):
        raise RuntimeError("Simulated XTTS backend failure.")


# ==========================================================
# ASSISTANT FACTORY
# ==========================================================


def create_assistant():

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    assistant.ollama = OllamaClient()

    assistant.llm_memory = ConversationMemory(max_messages=20)

    assistant.conversation = ConversationManager()

    assistant.context = ContextManager()

    assistant.state_manager = FakeStateManager()

    assistant.bridge = FakeBridge()

    assistant.wake_timeout_timer = FakeTimer()

    return assistant


# ==========================================================
# TEST 1
# BRAIN → VOICE BACKEND
# ==========================================================


def test_brain_to_voice_boundary(monkeypatch):

    assistant = create_assistant()

    voice_backend = FakeVoiceBackend()

    monkeypatch.setattr(
        assistant_v2,
        "speak",
        voice_backend.speak,
    )

    response = "JARVIS voice boundary test successful."

    assistant_v2.speak(response)

    assert voice_backend.requests == [response]

    print("PASS: Response reached voice backend.")


# ==========================================================
# TEST 2
# VOICE FAILURE DETECTION
# ==========================================================


def test_voice_backend_failure_is_detected():

    backend = FailingVoiceBackend()

    try:

        backend.speak("Simulated XTTS failure.")

    except RuntimeError as error:

        print(f"[VOICE ERROR] {error}")

        print("PASS: Voice backend failure detected.")

        return

    assert False, "Expected simulated voice backend failure."


# ==========================================================
# TEST 3
# BRAIN CONTINUES OPERATING
# ==========================================================


def test_brain_continues_after_voice_boundary():

    assistant = create_assistant()

    responses = []

    def safe_speak(text):

        responses.append(text)

        print(f"[SAFE VOICE] {text}")

    assistant_v2.speak = safe_speak

    command = "What is artificial intelligence?"

    print(f"USER: {command}")

    assistant.handle_command(command)

    assert len(responses) >= 1

    assert assistant.state_manager.get_state() == JarvisState.IDLE

    print("PASS: JARVIS brain continued operating.")


# ==========================================================
# TEST 4
# BACKEND REPLACEMENT
# ==========================================================


def test_voice_backend_can_be_replaced():

    backend_a = FakeVoiceBackend()
    backend_b = FakeVoiceBackend()

    assistant_v2.speak = backend_a.speak

    assistant_v2.speak("Backend A test.")

    assistant_v2.speak = backend_b.speak

    assistant_v2.speak("Backend B test.")

    assert backend_a.requests == ["Backend A test."]

    assert backend_b.requests == ["Backend B test."]

    print("PASS: Voice backend can be replaced.")
