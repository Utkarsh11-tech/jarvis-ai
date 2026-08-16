from brain.core import assistant_v2
from brain.core.context import ContextManager
from brain.core.conversation_manager import ConversationManager
from brain.memory.conversation_memory import ConversationMemory
from brain.models.ollama_client import OllamaClient

# ==========================================================
# FAKE TIMER
# ==========================================================


class FakeTimer:
    """
    Replaces QTimer during the isolated integration test.

    This allows Assistant V2 to run without starting the
    real Qt event loop.
    """

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
        self.current_state = None
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
# FAKE SPEAKER
# ==========================================================


def fake_speak(response):
    """
    Prevents the real XTTS/voice system from being called.

    XTTS is NOT required on this laptop.
    """

    print(f"[SPEAK] {response}")


# ==========================================================
# CREATE TEST ASSISTANT
# ==========================================================


def create_assistant():
    """
    Creates Assistant V2 without running the real Qt/GUI
    initialization.

    We manually provide the dependencies normally created
    by Assistant.__init__() / BaseAssistant.__init__().
    """

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    # ------------------------------------------------------
    # OLLAMA / QWEN
    # ------------------------------------------------------

    assistant.ollama = OllamaClient()

    # ------------------------------------------------------
    # LLM CONVERSATION MEMORY
    # ------------------------------------------------------

    assistant.llm_memory = ConversationMemory(max_messages=20)

    # ------------------------------------------------------
    # CONVERSATION MANAGER
    # ------------------------------------------------------

    assistant.conversation = ConversationManager()

    # ------------------------------------------------------
    # STATE MANAGER
    # ------------------------------------------------------

    assistant.state_manager = FakeStateManager()

    # ------------------------------------------------------
    # BRIDGE
    # ------------------------------------------------------

    assistant.bridge = FakeBridge()

    # ------------------------------------------------------
    # CONTEXT MANAGER
    #
    # IMPORTANT:
    # Base Assistant normally creates this inside
    # its __init__().
    # ------------------------------------------------------

    assistant.context = ContextManager()

    # ------------------------------------------------------
    # WAKE TIMEOUT TIMER
    # ------------------------------------------------------

    assistant.wake_timeout_timer = FakeTimer()

    return assistant


# ==========================================================
# MAIN TEST
# ==========================================================


def main():

    print("========================================")
    print("JARVIS HYBRID ASSISTANT TEST")
    print("========================================")

    # ======================================================
    # DISABLE REAL XTTS / VOICE OUTPUT
    # ======================================================

    assistant_v2.speak = fake_speak

    # ======================================================
    # CREATE ASSISTANT V2
    # ======================================================

    assistant = create_assistant()

    # ======================================================
    # TEST 1
    # UNKNOWN → QWEN
    # ======================================================

    print()
    print("----------------------------------------")
    print("TEST 1: UNKNOWN → QWEN")
    print("----------------------------------------")

    command = "What is machine learning?"

    print(f"USER: {command}")

    assistant.handle_command(command)

    # ======================================================
    # TEST 2
    # UNKNOWN → QWEN + MEMORY
    # ======================================================

    print()
    print("----------------------------------------")
    print("TEST 2: STORE MEMORY")
    print("----------------------------------------")

    command = "My name is Utkarsh. Remember that."

    print(f"USER: {command}")

    assistant.handle_command(command)

    # ======================================================
    # TEST 3
    # UNKNOWN → QWEN + MEMORY RECALL
    # ======================================================

    print()
    print("----------------------------------------")
    print("TEST 3: MEMORY RECALL")
    print("----------------------------------------")

    command = "What is my name?"

    print(f"USER: {command}")

    assistant.handle_command(command)

    # ======================================================
    # SHOW LLM MEMORY
    # ======================================================

    print()
    print("----------------------------------------")
    print("LLM MEMORY")
    print("----------------------------------------")

    messages = assistant.llm_memory.get_messages()

    for index, message in enumerate(
        messages,
        start=1,
    ):

        print(f"{index}. " f"{message['role']}: " f"{message['content']}")

    # ======================================================
    # TEST 4
    # KNOWN COMMAND → EXECUTOR
    # ======================================================

    print()
    print("----------------------------------------")
    print("TEST 4: KNOWN COMMAND → EXECUTOR")
    print("----------------------------------------")

    executor_calls = []

    # ------------------------------------------------------
    # Temporarily replace process_command.
    #
    # This guarantees a deterministic known command so
    # we can test the executor branch without opening
    # a real application.
    # ------------------------------------------------------

    assistant.process_command = lambda command: [
        {
            "intent": "OPEN_APPLICATION",
            "target": "calculator",
        }
    ]

    # ------------------------------------------------------
    # Prevent the real executor from opening Calculator.
    # ------------------------------------------------------

    original_execute = assistant_v2.execute

    def fake_execute(result):

        executor_calls.append(result)

        print("[EXECUTOR] " f"intent={result['intent']} " f"target={result['target']}")

        return "Calculator execution simulated."

    assistant_v2.execute = fake_execute

    # ------------------------------------------------------
    # Replace acknowledgement.
    # ------------------------------------------------------

    original_get_acknowledgement = assistant_v2.get_acknowledgement

    assistant_v2.get_acknowledgement = lambda result: "Opening Calculator."

    command = "Open calculator"

    print(f"USER: {command}")

    assistant.handle_command(command)

    # ------------------------------------------------------
    # Restore original functions.
    # ------------------------------------------------------

    assistant_v2.execute = original_execute

    assistant_v2.get_acknowledgement = original_get_acknowledgement

    # ======================================================
    # VALIDATION
    # ======================================================

    print()
    print("========================================")
    print("VALIDATION")
    print("========================================")

    # ------------------------------------------------------
    # MEMORY COUNT
    # ------------------------------------------------------

    if len(messages) == 6:

        print("PASS: Three LLM exchanges stored.")

    else:

        print("FAIL: Expected 6 LLM messages, " f"got {len(messages)}.")

    # ------------------------------------------------------
    # MEMORY ROLES
    # ------------------------------------------------------

    expected_roles = [
        "user",
        "assistant",
        "user",
        "assistant",
        "user",
        "assistant",
    ]

    actual_roles = [message["role"] for message in messages]

    if actual_roles == expected_roles:

        print("PASS: LLM memory roles are correct.")

    else:

        print("FAIL: LLM memory roles are incorrect.")

        print(f"Expected: {expected_roles}")

        print(f"Actual:   {actual_roles}")

    # ------------------------------------------------------
    # EXECUTOR
    # ------------------------------------------------------

    if len(executor_calls) == 1:

        result = executor_calls[0]

        if result["intent"] == "OPEN_APPLICATION" and result["target"] == "calculator":

            print("PASS: Known command reached executor.")

        else:

            print("FAIL: Incorrect executor result.")

    else:

        print("FAIL: Known command did not reach " "executor exactly once.")

    # ======================================================
    # FINAL RESULT
    # ======================================================

    llm_passed = len(messages) == 6 and actual_roles == expected_roles

    executor_passed = (
        len(executor_calls) == 1
        and executor_calls[0]["intent"] == "OPEN_APPLICATION"
        and executor_calls[0]["target"] == "calculator"
    )

    print()
    print("========================================")

    if llm_passed and executor_passed:

        print("HYBRID ROUTING TEST: PASSED")

    else:

        print("HYBRID ROUTING TEST: FAILED")

    print("========================================")


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()
