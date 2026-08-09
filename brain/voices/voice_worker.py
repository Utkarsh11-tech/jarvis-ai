from PySide6.QtCore import QObject, Signal

from brain.voices.listener import VoiceListener


class VoiceWorker(QObject):

    command_received = Signal(str)
    finished = Signal()

    def __init__(self):
        super().__init__()

        self.listener = None
        self.running = True

    def run(self):
        """
        Starts the voice listening loop.
        """

        self.listener = VoiceListener()

        print("JARVIS Voice Worker is ready.")

        try:

            while self.running:

                awakened = self.listener.listen_for_wake_word()

                if not awakened:
                    continue

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
