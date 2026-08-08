from pathlib import Path
import sys


# Add the project root to Python's import path when
# main.py is executed directly.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from brain.core.assistant import Assistant


def main():
    assistant = Assistant()
    assistant.start()


if __name__ == "__main__":
    main()