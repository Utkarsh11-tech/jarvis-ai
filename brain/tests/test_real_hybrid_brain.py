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


def fake_speak(response):

    print(f"[SPEAK] {response}")


# ==========================================================
# CREATE ISOLATED ASSISTANT
# ==========================================================


def create_assistant():

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    # ------------------------------------------------------
    # LLM
    # ------------------------------------------------------

    assistant.ollama = OllamaClient()

    # ------------------------------------------------------
    # LLM MEMORY
    # ------------------------------------------------------

    assistant.llm_memory = ConversationMemory(max_messages=20)

    # ------------------------------------------------------
    # CONVERSATION MANAGER
    # ------------------------------------------------------

    assistant.conversation = ConversationManager()

    # ------------------------------------------------------
    # CONTEXT MANAGER
    # ------------------------------------------------------

    assistant.context = ContextManager()

    # ------------------------------------------------------
    # STATE MANAGER
    # ------------------------------------------------------

    assistant.state_manager = FakeStateManager()

    # ------------------------------------------------------
    # BRIDGE
    # ------------------------------------------------------

    assistant.bridge = FakeBridge()

    # ------------------------------------------------------
    # TIMER
    # ------------------------------------------------------

    assistant.wake_timeout_timer = FakeTimer()

    return assistant


# ==========================================================
# HELPER
# ==========================================================


def section(title):

    print()
    print("----------------------------------------")
    print(title)
    print("----------------------------------------")


# ==========================================================
# MAIN TEST
# ==========================================================


def main():

    print("========================================")
    print("JARVIS REAL HYBRID BRAIN TEST")
    print("========================================")

    # ======================================================
    # DISABLE XTTS
    # ======================================================

    assistant_v2.speak = fake_speak

    # ======================================================
    # CREATE ASSISTANT
    # ======================================================

    assistant = create_assistant()

    # ======================================================
    # TEST 1
    # CONVERSATIONAL INPUT → QWEN
    # ======================================================

    section("TEST 1: CONVERSATION → QWEN")

    command = "Explain artificial intelligence " "in one simple sentence."

    print(f"USER: {command}")

    assistant.handle_command(command)

    # ======================================================
    # TEST 2
    # MEMORY STORAGE
    # ======================================================

    section("TEST 2: MEMORY STORAGE")

    command = "My name is Utkarsh. Remember that."

    print(f"USER: {command}")

    assistant.handle_command(command)

    # ======================================================
    # TEST 3
    # MEMORY RECALL
    # ======================================================

    section("TEST 3: MEMORY RECALL")

    command = "What is my name?"

    print(f"USER: {command}")

    assistant.handle_command(command)

    # ======================================================
    # SHOW MEMORY
    # ======================================================

    section("LLM MEMORY")

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

    section("TEST 4: KNOWN COMMAND → EXECUTOR")

    executor_calls = []

    original_execute = assistant_v2.execute

    original_ack = assistant_v2.get_acknowledgement

    # ------------------------------------------------------
    # Replace executor temporarily.
    # ------------------------------------------------------

    def fake_execute(result):

        executor_calls.append(result)

        print("[EXECUTOR] " f"{result['intent']} " f"→ {result['target']}")

        return "Calculator execution simulated."

    assistant_v2.execute = fake_execute

    assistant_v2.get_acknowledgement = lambda result: "Opening Calculator."

    command = "Open calculator"

    print(f"USER: {command}")

    assistant.handle_command(command)

    # ------------------------------------------------------
    # Restore acknowledgement only after test.
    # ------------------------------------------------------

    assistant_v2.get_acknowledgement = original_ack

    # ======================================================
    # TEST 5
    # SHUTDOWN → CONFIRMATION
    # ======================================================

    section("TEST 5: SHUTDOWN → CONFIRMATION")

    shutdown_calls = []

    original_shutdown = assistant._execute_confirmed_action

    def fake_confirmed_action(
        action,
        action_data,
    ):

        shutdown_calls.append(action)

        print(f"[SYSTEM ACTION] {action}")

        return "Shutdown simulated."

    assistant._execute_confirmed_action = fake_confirmed_action

    command = "shutdown"

    print(f"USER: {command}")

    assistant.handle_command(command)

    # ======================================================
    # TEST 6
    # CANCEL SHUTDOWN
    # ======================================================

    section("TEST 6: CANCEL CONFIRMATION")

    command = "no"

    print(f"USER: {command}")

    assistant.handle_command(command)

    # ------------------------------------------------------
    # Restore confirmation handler.
    # ------------------------------------------------------

    assistant._execute_confirmed_action = original_shutdown

    # ------------------------------------------------------
    # Restore executor.
    # ------------------------------------------------------

    assistant_v2.execute = original_execute

    # ======================================================
    # VALIDATION
    # ======================================================

    section("VALIDATION")

    passed = True

    # ------------------------------------------------------
    # MEMORY
    # ------------------------------------------------------

    if len(messages) == 6:

        print("PASS: Six LLM messages stored.")

    else:

        print("FAIL: Expected 6 LLM messages.")

        print(f"Actual count: {len(messages)}")

        passed = False

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

        print("PASS: Conversation roles correct.")

    else:

        print("FAIL: Conversation roles incorrect.")

        passed = False

    # ------------------------------------------------------
    # EXECUTOR
    # ------------------------------------------------------

    if len(executor_calls) == 1:

        result = executor_calls[0]

        if result["intent"] == "OPEN_APPLICATION" and result["target"] == "calculator":

            print("PASS: Known command reached executor.")

        else:

            print("FAIL: Wrong executor command.")

            passed = False

    else:

        print("FAIL: Executor was not called exactly once.")

        passed = False

    # ------------------------------------------------------
    # SHUTDOWN CONFIRMATION
    # ------------------------------------------------------

    if shutdown_calls == []:

        print("PASS: Shutdown was not executed " "before confirmation.")

    else:

        print("FAIL: Shutdown executed without confirmation.")

        passed = False

    # ------------------------------------------------------
    # CONFIRMATION STATE
    # ------------------------------------------------------

    if JarvisState.THINKING in assistant.state_manager.states:

        print("PASS: Thinking state reached.")

    else:

        print("FAIL: Thinking state was not reached.")

        passed = False

    # ------------------------------------------------------
    # FINAL STATE
    # ------------------------------------------------------

    if assistant.state_manager.get_state() == JarvisState.IDLE:

        print("PASS: JARVIS returned to IDLE.")

    else:

        print("FAIL: JARVIS did not return to IDLE.")

        passed = False

    # ======================================================
    # FINAL RESULT
    # ======================================================

    print()
    print("========================================")

    if passed:

        print("REAL HYBRID BRAIN TEST: PASSED")

    else:

        print("REAL HYBRID BRAIN TEST: FAILED")

    print("========================================")


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()
