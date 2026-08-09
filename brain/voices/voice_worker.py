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

        # Listen for one-time follow-up requests.
        self.bridge.voice_input_requested.connect(self.listen_for_follow_up)

    # ==================================================
    # MAIN VOICE LOOP
    # ==================================================

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

    # ==================================================
    # FOLLOW-UP VOICE INPUT
    # ==================================================

    def listen_for_follow_up(self):
        """
        Listens for one command without requiring
        the wake word.

        Used for follow-up interactions such as
        Chrome profile selection.
        """

        if not self.running:
            return

        if not self.listener:
            return

        self.bridge.set_state(JarvisState.LISTENING.value)

        print("JARVIS: Waiting for your response...")

        response = self.listener.listen_for_command()

        if response:

            print(f"You said: {response}")

            self.command_received.emit(response)

    # ==================================================
    # STOP
    # ==================================================

    def stop(self):
        """
        Stops the voice worker.
        """

        self.running = False

        if self.listener:

            self.listener.stop()
