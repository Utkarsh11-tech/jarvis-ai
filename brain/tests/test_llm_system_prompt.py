from brain.config.llm_config import JARVIS_SYSTEM_PROMPT
from brain.models.ollama_client import OllamaClient


def main():
    print("========================================")
    print("JARVIS SYSTEM PROMPT TEST")
    print("========================================")

    client = OllamaClient()

    prompt = (
        "Introduce yourself in one short sentence "
        "and tell me what you are designed to do."
    )

    print()
    print(f"USER: {prompt}")
    print()
    print("Sending system prompt to Qwen...")

    try:

        response = client.generate(
            prompt=prompt,
            system_prompt=JARVIS_SYSTEM_PROMPT,
        )

    except RuntimeError as error:

        print()
        print("========================================")
        print("TEST FAILED")
        print("========================================")
        print(error)

        return

    print()
    print("QWEN RESPONSE:")
    print(response)

    print()
    print("========================================")
    print("TEST COMPLETE")
    print("========================================")


if __name__ == "__main__":
    main()
