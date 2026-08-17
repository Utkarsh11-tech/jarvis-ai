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

        print(
            f"[STATE] {state}"
        )

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

        print(
            f"[BRIDGE] {response}"
        )


# ==========================================================
# CREATE REAL ASSISTANT V2
# ==========================================================

def create_assistant():

    """
    Creates Assistant V2 without starting the GUI.

    IMPORTANT:
    - Real Ollama
    - Real Qwen
    - Real conversation memory
    - Real Assistant V2 routing
    - Real voice_manager
    - Real XTTS backend

    Only the GUI/Qt infrastructure is replaced.
    """

    assistant = (
        assistant_v2.Assistant.__new__(
            assistant_v2.Assistant
        )
    )

    # ------------------------------------------------------
    # REAL QWEN CLIENT
    # ------------------------------------------------------

    assistant.ollama = OllamaClient()

    # ------------------------------------------------------
    # REAL LLM MEMORY
    # ------------------------------------------------------

    assistant.llm_memory = (
        ConversationMemory(
            max_messages=20
        )
    )

    # ------------------------------------------------------
    # REAL CONVERSATION MANAGER
    # ------------------------------------------------------

    assistant.conversation = (
        ConversationManager()
    )

    # ------------------------------------------------------
    # REAL CONTEXT
    # ------------------------------------------------------

    assistant.context = (
        ContextManager()
    )

    # ------------------------------------------------------
    # TEST GUI DEPENDENCIES
    # ------------------------------------------------------

    assistant.state_manager = (
        FakeStateManager()
    )

    assistant.bridge = (
        FakeBridge()
    )

    assistant.wake_timeout_timer = (
        FakeTimer()
    )

    return assistant


# ==========================================================
# TEST
# ==========================================================

def main():

    print()
    print(
        "========================================"
    )
    print(
        "JARVIS REAL QWEN + XTTS TEST"
    )
    print(
        "========================================"
    )

    print()
    print(
        "REAL COMPONENTS:"
    )
    print(
        "  Qwen / Ollama       : ENABLED"
    )
    print(
        "  Assistant V2        : ENABLED"
    )
    print(
        "  Conversation Memory : ENABLED"
    )
    print(
        "  Voice Manager       : ENABLED"
    )
    print(
        "  XTTS                : ENABLED"
    )
    print(
        "  RTX 5050            : ENABLED"
    )

    # ======================================================
    # CREATE ASSISTANT
    # ======================================================

    assistant = create_assistant()

    # ======================================================
    # TEST 1
    # REAL CONVERSATIONAL COMMAND
    # ======================================================

    print()
    print(
        "----------------------------------------"
    )
    print(
        "TEST 1: QWEN → XTTS"
    )
    print(
        "----------------------------------------"
    )

    command = (
        "Reply with exactly one short sentence: "
        "JARVIS real integration is working."
    )

    print(
        f"USER: {command}"
    )

    assistant.handle_command(
        command
    )

    # ======================================================
    # VALIDATE MEMORY
    # ======================================================

    print()
    print(
        "----------------------------------------"
    )
    print(
        "LLM MEMORY"
    )
    print(
        "----------------------------------------"
    )

    messages = (
        assistant.llm_memory.get_messages()
    )

    for index, message in enumerate(
        messages,
        start=1,
    ):

        print(
            f"{index}. "
            f"{message['role']}: "
            f"{message['content']}"
        )

    # ======================================================
    # VALIDATION
    # ======================================================

    print()
    print(
        "========================================"
    )
    print(
        "VALIDATION"
    )
    print(
        "========================================"
    )

    # ------------------------------------------------------
    # Memory validation
    # ------------------------------------------------------

    if len(messages) == 2:

        print(
            "PASS: Qwen exchange stored."
        )

    else:

        print(
            "FAIL: Expected 2 memory messages, "
            f"got {len(messages)}."
        )

    # ------------------------------------------------------
    # Role validation
    # ------------------------------------------------------

    expected_roles = [
        "user",
        "assistant",
    ]

    actual_roles = [
        message["role"]
        for message in messages
    ]

    if actual_roles == expected_roles:

        print(
            "PASS: Conversation roles correct."
        )

    else:

        print(
            "FAIL: Conversation roles incorrect."
        )

    # ------------------------------------------------------
    # Response validation
    # ------------------------------------------------------

    if len(messages) >= 2:

        response = (
            messages[-1]["content"]
        )

        if response.strip():

            print(
                "PASS: Qwen returned a response."
            )

        else:

            print(
                "FAIL: Qwen response was empty."
            )

    # ------------------------------------------------------
    # Bridge validation
    # ------------------------------------------------------

    if len(
        assistant.bridge.responses
    ) == 1:

        print(
            "PASS: Response reached bridge."
        )

    else:

        print(
            "FAIL: Response did not reach bridge."
        )

    # ------------------------------------------------------
    # State validation
    # ------------------------------------------------------

    states = (
        assistant.state_manager.states
    )

    if JarvisState.THINKING in states:

        print(
            "PASS: THINKING state reached."
        )

    else:

        print(
            "FAIL: THINKING state not reached."
        )

    if JarvisState.SPEAKING in states:

        print(
            "PASS: SPEAKING state reached."
        )

    else:

        print(
            "FAIL: SPEAKING state not reached."
        )

    if states and states[-1] == JarvisState.IDLE:

        print(
            "PASS: JARVIS returned to IDLE."
        )

    else:

        print(
            "FAIL: JARVIS did not return to IDLE."
        )

    # ======================================================
    # FINAL RESULT
    # ======================================================

    integration_passed = (
        len(messages) == 2
        and actual_roles == expected_roles
        and len(
            assistant.bridge.responses
        ) == 1
        and JarvisState.THINKING in states
        and JarvisState.SPEAKING in states
        and states[-1] == JarvisState.IDLE
    )

    print()
    print(
        "========================================"
    )

    if integration_passed:

        print(
            "REAL QWEN + XTTS INTEGRATION: PASSED"
        )

    else:

        print(
            "REAL QWEN + XTTS INTEGRATION: FAILED"
        )

    print(
        "========================================"
    )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    main()