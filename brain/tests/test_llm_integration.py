from brain.core import assistant_v2


class FakeStateManager:
    def set_state(self, state):
        print(f"[STATE] {state}")


class FakeBridge:
    def send_response(self, response):
        print(f"[BRIDGE] {response}")


def fake_speak(response):
    print(f"[SPEAK] {response}")


def main():
    print("========================================")
    print("JARVIS LLM INTEGRATION TEST")
    print("========================================")

    # Disable real TTS for this test.
    # XTTS is NOT required.
    assistant_v2.speak = fake_speak

    # Create Assistant V2 without starting the
    # normal GUI / voice infrastructure.
    assistant = assistant_v2.Assistant.__new__(assistant_v2.Assistant)

    # Provide only the components required by
    # _handle_llm_command().
    assistant.ollama = assistant_v2.OllamaClient()

    assistant.state_manager = FakeStateManager()

    assistant.bridge = FakeBridge()

    # Test command.
    command = "Explain what machine learning is " "in one simple sentence."

    print()
    print(f"USER: {command}")
    print()

    print("Sending command to Assistant V2...")

    try:

        result = assistant._handle_llm_command(command)

    except Exception as error:

        print()
        print("========================================")
        print("TEST FAILED")
        print("========================================")
        print(f"{type(error).__name__}: {error}")

        return

    print()
    print("========================================")
    print("TEST RESULT")
    print("========================================")
    print(f"Returned: {result}")
    print("========================================")


if __name__ == "__main__":
    main()
