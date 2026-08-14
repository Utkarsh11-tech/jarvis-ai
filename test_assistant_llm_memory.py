from brain.core import assistant_v2
from brain.core.state import JarvisState
from brain.memory.conversation_memory import ConversationMemory
from brain.models.ollama_client import OllamaClient


class FakeStateManager:
    def __init__(self):
        self.current_state = None

    def set_state(self, state):
        self.current_state = state
        print(f"[STATE] {state}")

    def get_state(self):
        return self.current_state


class FakeBridge:
    def send_response(self, response):
        print(f"[BRIDGE] {response}")


def fake_speak(response):
    print(f"[SPEAK] {response}")


def main():
    print("========================================")
    print("JARVIS ASSISTANT V2 MEMORY TEST")
    print("========================================")

    # --------------------------------------------------
    # Disable real TTS.
    # XTTS is NOT required.
    # --------------------------------------------------

    assistant_v2.speak = fake_speak

    # --------------------------------------------------
    # Create Assistant V2 without starting the
    # normal GUI / voice infrastructure.
    # --------------------------------------------------

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    # --------------------------------------------------
    # Required components
    # --------------------------------------------------

    assistant.ollama = OllamaClient()

    assistant.llm_memory = ConversationMemory(max_messages=20)

    assistant.state_manager = FakeStateManager()

    assistant.bridge = FakeBridge()

    # ==================================================
    # FIRST MESSAGE
    # ==================================================

    first_command = "My name is Utkarsh. Remember that."

    print()
    print("----------------------------------------")
    print("FIRST MESSAGE")
    print("----------------------------------------")
    print(f"USER: {first_command}")
    print()

    result = assistant._handle_llm_command(first_command)

    print()
    print(f"Returned: {result}")

    # ==================================================
    # SHOW MEMORY AFTER FIRST MESSAGE
    # ==================================================

    print()
    print("----------------------------------------")
    print("MEMORY AFTER FIRST MESSAGE")
    print("----------------------------------------")

    for message in assistant.llm_memory.get_messages():

        print(f"{message['role']}: " f"{message['content']}")

    # ==================================================
    # SECOND MESSAGE
    # ==================================================

    second_command = "What is my name?"

    print()
    print("----------------------------------------")
    print("SECOND MESSAGE")
    print("----------------------------------------")
    print(f"USER: {second_command}")
    print()

    result = assistant._handle_llm_command(second_command)

    print()
    print(f"Returned: {result}")

    # ==================================================
    # FINAL MEMORY
    # ==================================================

    print()
    print("----------------------------------------")
    print("FINAL LLM MEMORY")
    print("----------------------------------------")

    messages = assistant.llm_memory.get_messages()

    for message in messages:

        print(f"{message['role']}: " f"{message['content']}")

    # ==================================================
    # VALIDATION
    # ==================================================

    print()
    print("----------------------------------------")
    print("VALIDATION")
    print("----------------------------------------")

    if len(messages) == 4:

        print("PASS: Four conversation messages stored.")

    else:

        print("FAIL: Expected 4 messages, " f"got {len(messages)}.")

    roles = [message["role"] for message in messages]

    expected_roles = [
        "user",
        "assistant",
        "user",
        "assistant",
    ]

    if roles == expected_roles:

        print("PASS: Conversation roles are correct.")

    else:

        print("FAIL: Conversation roles are incorrect.")

    print()
    print("========================================")
    print("TEST COMPLETE")
    print("========================================")


if __name__ == "__main__":
    main()
