from brain.memory.conversation_memory import (
    ConversationMemory,
)


def main():
    print("========================================")
    print("JARVIS CONVERSATION MEMORY TEST")
    print("========================================")

    memory = ConversationMemory(max_messages=4)

    print()
    print("Adding conversation...")

    memory.add_user_message("My name is Utkarsh.")

    memory.add_assistant_message("Nice to meet you, Utkarsh.")

    memory.add_user_message("I am building JARVIS.")

    memory.add_assistant_message("That sounds interesting.")

    print()
    print(f"Message count: " f"{memory.get_message_count()}")

    print()
    print("Conversation:")

    for message in memory.get_messages():

        print(f"{message['role']}: " f"{message['content']}")

    print()
    print("Testing automatic trimming...")

    memory.add_user_message("Remember this message.")

    print(
        f"Message count after adding "
        f"another message: "
        f"{memory.get_message_count()}"
    )

    print()
    print("Recent messages:")

    for message in memory.get_recent_messages(2):

        print(f"{message['role']}: " f"{message['content']}")

    print()
    print("Testing clear...")

    memory.clear()

    print(f"Message count after clear: " f"{memory.get_message_count()}")

    print()
    print("========================================")
    print("TEST COMPLETE")
    print("========================================")


if __name__ == "__main__":
    main()
