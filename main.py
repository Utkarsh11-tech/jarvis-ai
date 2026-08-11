import sys

from PySide6.QtCore import QThread, Qt
from PySide6.QtWidgets import QApplication

from bridge.bridge import JarvisBridge

from brain.core.assistant_v2 import Assistant
from brain.voices.voice_worker import VoiceWorker

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

    brain_thread = QThread()

    assistant.moveToThread(brain_thread)

    brain_thread.started.connect(
        assistant.run
    )

    brain_thread.start()

    # ================================================
    # VOICE WORKER
    # ================================================

    voice_worker = VoiceWorker(bridge)

    voice_thread = QThread()

    voice_worker.moveToThread(
        voice_thread
    )

    # --------------------------------
    # Voice → Bridge
    # --------------------------------

    voice_worker.command_received.connect(
        bridge.send_command
    )

    # --------------------------------
    # Bridge → Voice Worker
    # Request one-time follow-up input
    # --------------------------------

    bridge.voice_input_requested.connect(
        voice_worker.request_follow_up,
        Qt.DirectConnection,
    )

    # --------------------------------
    # Voice Worker shutdown
    # --------------------------------

    voice_worker.finished.connect(
        voice_thread.quit
    )

    voice_thread.started.connect(
        voice_worker.run
    )

    voice_thread.start()

    # ================================================
    # START APPLICATION
    # ================================================

    exit_code = app.exec()

    # ================================================
    # SHUTDOWN
    # ================================================

    voice_worker.stop()

    voice_thread.quit()
    voice_thread.wait()

    brain_thread.quit()
    brain_thread.wait()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()