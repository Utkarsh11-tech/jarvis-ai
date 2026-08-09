from brain.core.normalizer import normalize
from brain.core.intent_detector import detect_intent
from brain.core.target_extractor import extract_target
from brain.core.executor import execute


def main():

    command = normalize("run automation test")

    words = command.split()

    action = words[0]

    target = extract_target(words)

    intent = detect_intent(
        action,
        target,
    )

    result = {
        "intent": intent,
        "target": target,
    }

    print("Command:", command)
    print("Action:", action)
    print("Target:", target)
    print("Intent:", intent)

    print("\nExecuting...")

    response = execute(result)

    print("JARVIS:", response)


if __name__ == "__main__":
    main()
