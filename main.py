import sys

from PySide6.QtCore import QThread
from PySide6.QtWidgets import QApplication

from bridge.bridge import JarvisBridge

from brain.core.assistant import Assistant

from body.app.screens.home.home_screen import MainWindow


def main():

    # ================================================
    # APPLICATION
    # ================================================

    app = QApplication(sys.argv)

    # ================================================
    # SHARED BRIDGE
    # ================================================

    bridge = JarvisBridge()

    # ================================================
    # BODY
    # ================================================

    window = MainWindow(bridge)
    window.show()

    # ================================================
    # BRAIN
    # ================================================

    assistant = Assistant(bridge)

    # ================================================
    # BRAIN THREAD
    # ================================================

    brain_thread = QThread()

    assistant.moveToThread(brain_thread)

    brain_thread.started.connect(assistant.start)

    brain_thread.start()

    # ================================================
    # START APPLICATION
    # ================================================

    exit_code = app.exec()

    # ================================================
    # SHUTDOWN
    # ================================================

    brain_thread.quit()
    brain_thread.wait()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
