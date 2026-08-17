import os

from brain.models.ollama_client import OllamaClient

# ==========================================================
# TEST CONFIGURATION
# ==========================================================

EXPECTED_MODEL = "qwen3:8b"

EXPECTED_BASE_URL = "http://localhost:11434"


# ==========================================================
# TEST 1
# OLLAMA SERVER
# ==========================================================


def test_ollama_server_is_available():

    client = OllamaClient()

    print()
    print("========================================")
    print("JARVIS LLM RUNTIME TEST")
    print("========================================")

    print()
    print("----------------------------------------")
    print("TEST 1: OLLAMA SERVER")
    print("----------------------------------------")

    print(f"Server : {client.get_base_url()}")

    available = client.is_available()

    print(f"Available: {available}")

    assert available, "Ollama server is not available."


# ==========================================================
# TEST 2
# MODEL
# ==========================================================


def test_ollama_model_is_available():

    client = OllamaClient()

    print()
    print("----------------------------------------")
    print("TEST 2: OLLAMA MODEL")
    print("----------------------------------------")

    print(f"Model : {client.get_model()}")

    assert client.get_model() == EXPECTED_MODEL, (
        "Unexpected Ollama model. "
        f"Expected '{EXPECTED_MODEL}', "
        f"got '{client.get_model()}'."
    )

    available = client.has_model()

    print(f"Model available: {available}")

    assert available, f"Ollama model '{EXPECTED_MODEL}' " "is not available."


# ==========================================================
# TEST 3
# CONFIGURATION
# ==========================================================


def test_ollama_configuration():

    client = OllamaClient()

    print()
    print("----------------------------------------")
    print("TEST 3: OLLAMA CONFIGURATION")
    print("----------------------------------------")

    print(f"Base URL : {client.get_base_url()}")

    print(f"Model    : {client.get_model()}")

    print(f"Timeout  : {client.get_timeout()} seconds")

    assert client.get_base_url() == EXPECTED_BASE_URL, "Unexpected Ollama base URL."

    assert client.get_timeout() > 0, "Ollama timeout must be greater than zero."


# ==========================================================
# TEST 4
# REAL QWEN GENERATION
# ==========================================================


def test_real_qwen_generation():

    client = OllamaClient()

    print()
    print("----------------------------------------")
    print("TEST 4: REAL QWEN GENERATION")
    print("----------------------------------------")

    prompt = "Reply with exactly: JARVIS online."

    print(f"USER: {prompt}")

    response = client.generate(
        prompt=prompt,
    )

    print()
    print(f"QWEN: {response}")

    assert response, "Qwen returned an empty response."

    assert isinstance(
        response,
        str,
    ), "Qwen response must be a string."


# ==========================================================
# TEST 5
# CONVERSATION HISTORY
# ==========================================================


def test_real_qwen_history():

    client = OllamaClient()

    print()
    print("----------------------------------------")
    print("TEST 5: REAL QWEN HISTORY")
    print("----------------------------------------")

    history = [
        {
            "role": "user",
            "content": ("My name is Utkarsh."),
        },
        {
            "role": "assistant",
            "content": ("Nice to meet you, Utkarsh."),
        },
    ]

    prompt = "What is my name? " "Answer with only the name."

    print(f"USER: {prompt}")

    response = client.generate(
        prompt=prompt,
        history=history,
    )

    print()
    print(f"QWEN: {response}")

    assert response, "Qwen returned an empty response."

    assert "utkarsh" in response.lower(), (
        "Qwen did not correctly use " "the supplied conversation history."
    )


# ==========================================================
# FINAL SUMMARY
# ==========================================================


def test_runtime_summary():

    client = OllamaClient()

    print()
    print("========================================")
    print("LLM RUNTIME SUMMARY")
    print("========================================")

    print(f"Server : {client.get_base_url()}")

    print(f"Model  : {client.get_model()}")

    print(f"Timeout: {client.get_timeout()} seconds")

    print()
    print("LLM runtime preflight completed.")

    print("========================================")
