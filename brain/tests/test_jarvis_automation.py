
from brain.core.executor import execute


def main():

    command = {
        "intent": "UI_AUTOMATION",
        "target": "automation_test",
    }

    print(
        "JARVIS:",
        execute(command),
    )


if __name__ == "__main__":
    main()

