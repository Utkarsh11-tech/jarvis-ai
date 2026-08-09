from PySide6.QtCore import QObject, Signal

from brain.voices.listener import VoiceListener
from bridge.bridge import JarvisBridge

from brain.core.state import JarvisState


class VoiceWorker(QObject):

    command_received = Signal(str)
    finished = Signal()

    def __init__(self, bridge):
        super().__init__()

        self.listener = None
        self.running = True
        self.bridge = bridge

    def run(self):
        """
        Starts the voice listening loop.
        """

        self.listener = VoiceListener()

        print("JARVIS Voice Worker is ready.")

        try:

            while self.running:

                # -------------------------
                # SLEEPING
                # -------------------------

                self.bridge.set_state(JarvisState.SLEEPING.value)

                awakened = self.listener.listen_for_wake_word()

                if not awakened:
                    continue

                # -------------------------
                # LISTENING
                # -------------------------

                self.bridge.set_state(JarvisState.LISTENING.value)

                command = self.listener.listen_for_command()

                if command:
                    self.command_received.emit(command)

                self.listener.prepare_for_wake_word()

        finally:

            if self.listener:
                self.listener.close()

            self.finished.emit()

    def stop(self):
        """
        Stops the voice worker.
        """

        self.running = False

        if self.listener:
            self.listener.stop()
