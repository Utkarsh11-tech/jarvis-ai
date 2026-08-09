
from pathlib import Path

from brain.automation.ui_monitor import (
    UIElementMonitor,
)


def main():

    monitor = UIElementMonitor()

    try:

        html_file = (
            Path(__file__)
            .parent
            / "automation_test.html"
        )

        url = html_file.resolve().as_uri()

        print(
            "JARVIS: Opening automation test..."
        )

        monitor.open_page(url)

        print(
            "JARVIS: Waiting for the action..."
        )

        success = monitor.wait_and_click(
            "#test-button"
        )

        if success:

            print(
                "JARVIS: Action completed successfully."
            )

        else:

            print(
                "JARVIS: Action failed."
            )

        input(
            "\nPress Enter to close..."
        )

    finally:

        monitor.close()


if __name__ == "__main__":
    main()
