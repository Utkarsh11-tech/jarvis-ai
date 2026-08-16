from brain.core import assistant_v2
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


def run_command(assistant, command):
    print()
    print("----------------------------------------")
    print(f"USER: {command}")
    print("----------------------------------------")

    result = assistant._handle_llm_command(command)

    print()
    print(f"Returned: {result}")

    return result


def main():
    print("========================================")
    print("JARVIS FULL BRAIN TEST")
    print("========================================")

    # ==================================================
    # DISABLE REAL TTS
    # ==================================================

    assistant_v2.speak = fake_speak

    # ==================================================
    # CREATE ASSISTANT V2 WITHOUT GUI / VOICE
    # ==================================================

    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    # ==================================================
    # REQUIRED COMPONENTS
    # ==================================================

    assistant.ollama = OllamaClient()

    assistant.llm_memory = ConversationMemory(max_messages=20)

    assistant.state_manager = FakeStateManager()

    assistant.bridge = FakeBridge()

    # ==================================================
    # TEST 1 — JARVIS IDENTITY
    # ==================================================

    run_command(assistant, "Who are you?")

    # ==================================================
    # TEST 2 — MEMORY
    # ==================================================

    run_command(assistant, "My name is Utkarsh. Remember that.")

    # ==================================================
    # TEST 3 — MEMORY RECALL
    # ==================================================

    run_command(assistant, "What is my name?")

    # ==================================================
    # TEST 4 — CONTEXTUAL FOLLOW-UP
    # ==================================================

    run_command(assistant, "What can you help me with?")

    # ==================================================
    # SHOW FINAL MEMORY
    # ==================================================

    print()
    print("========================================")
    print("FINAL CONVERSATION MEMORY")
    print("========================================")

    messages = assistant.llm_memory.get_messages()

    for index, message in enumerate(
        messages,
        start=1,
    ):

        print(f"{index}. " f"{message['role']}: " f"{message['content']}")

    # ==================================================
    # VALIDATION
    # ==================================================

    print()
    print("========================================")
    print("VALIDATION")
    print("========================================")

    expected_message_count = 8

    if len(messages) == expected_message_count:

        print("PASS: 4 user/assistant exchanges " "were stored.")

    else:

        print(
            "WARNING: Expected "
            f"{expected_message_count} messages, "
            f"got {len(messages)}."
        )

    roles = [message["role"] for message in messages]

    expected_roles = [
        "user",
        "assistant",
        "user",
        "assistant",
        "user",
        "assistant",
        "user",
        "assistant",
    ]

    if roles == expected_roles:

        print("PASS: Conversation roles are correct.")

    else:

        print("WARNING: Conversation roles " "are incorrect.")

    print()
    print("========================================")
    print("TEST COMPLETE")
    print("========================================")


if __name__ == "__main__":
    main()
