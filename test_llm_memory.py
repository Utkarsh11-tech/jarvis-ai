from brain.memory.conversation_memory import (
    ConversationMemory,
)
from brain.models.ollama_client import (
    OllamaClient,
)


def main():
    print("========================================")
    print("JARVIS LLM MEMORY TEST")
    print("========================================")

    memory = ConversationMemory(max_messages=10)

    client = OllamaClient()

    # ==================================================
    # FIRST MESSAGE
    # ==================================================

    first_message = "My name is Utkarsh. " "Remember that."

    print()
    print(f"USER: {first_message}")
    print()
    print("Sending first message to Qwen...")

    try:

        first_response = client.generate(
            prompt=first_message,
            history=memory.get_messages(),
        )

    except RuntimeError as error:

        print()
        print("TEST FAILED")
        print(error)

        return

    print()
    print(f"QWEN: {first_response}")

    memory.add_user_message(first_message)

    memory.add_assistant_message(first_response)

    # ==================================================
    # SECOND MESSAGE
    # ==================================================

    second_message = "What is my name?"

    print()
    print("----------------------------------------")
    print()
    print(f"USER: {second_message}")
    print()
    print("Sending conversation history to Qwen...")

    try:

        second_response = client.generate(
            prompt=second_message,
            history=memory.get_messages(),
        )

    except RuntimeError as error:

        print()
        print("TEST FAILED")
        print(error)

        return

    print()
    print(f"QWEN: {second_response}")

    memory.add_user_message(second_message)

    memory.add_assistant_message(second_response)

    # ==================================================
    # SHOW MEMORY
    # ==================================================

    print()
    print("----------------------------------------")
    print("STORED CONVERSATION")
    print("----------------------------------------")

    for message in memory.get_messages():

        print(f"{message['role']}: " f"{message['content']}")

    print()
    print("========================================")
    print("TEST COMPLETE")
    print("========================================")


if __name__ == "__main__":
    main()
