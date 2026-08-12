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

    # Voice-recognized commands use the same conversation UI
    # as typed commands. Keeping this connection at the application
    # boundary avoids coupling the voice worker to the UI widgets.
    bridge.transcript_received.connect(
        window.chat.add_user_message
    )

    # The overlay owns its presentation, while the bridge owns
    # the event flow. This keeps the voice worker UI-agnostic.
    bridge.overlay_status_changed.connect(
        window.overlay.set_status
    )

    # Keep the floating overlay useful during the complete interaction,
    # not only the initial listening state. The home screen still controls
    # its normal wake-word lifecycle; these updates add the processing and
    # speaking states without changing the existing voice pipeline.
    def update_overlay_for_state(state):
        normalized = str(state).lower()

        if normalized == "thinking":
            window.overlay.set_status("Processing...")
            window.show_wake_overlay()

        elif normalized == "executing":
            window.overlay.set_status("Processing...")
            window.show_wake_overlay()

        elif normalized == "speaking":
            window.overlay.set_status("Speaking...")
            window.show_wake_overlay()

        elif normalized == "error":
            window.overlay.set_status("Error")
            window.show_wake_overlay()

        elif normalized == "sleeping":
            window.overlay.hide_overlay()

    bridge.state_changed.connect(
        update_overlay_for_state
    )

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
