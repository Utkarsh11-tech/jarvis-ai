from brain.models.ollama_client import OllamaClient


def main():

    client = OllamaClient()

    print("========================================")
    print("JARVIS OLLAMA TEST")
    print("========================================")

    print(f"Server : {client.get_base_url()}")

    print(f"Model  : {client.get_model()}")

    print()

    print("Checking Ollama...")

    if not client.is_available():

        print("ERROR: Ollama is not available.")

        return

    print("Ollama is available.")

    print()

    print("Checking model...")

    if not client.has_model():

        print(f"ERROR: Model '{client.get_model()}' " "was not found.")

        return

    print(f"Model '{client.get_model()}' is available.")

    print()

    print("Sending test prompt...")

    try:

        response = client.generate("Respond with exactly: JARVIS online.")

        print()
        print("QWEN RESPONSE:")
        print(response)

    except RuntimeError as error:

        print()
        print("ERROR:")
        print(error)

    print()
    print("========================================")


if __name__ == "__main__":
    main()
