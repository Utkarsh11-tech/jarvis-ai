import threading

from PySide6.QtCore import QObject, Signal

from brain.voices.listener import VoiceListener
from brain.core.state import JarvisState


class VoiceWorker(QObject):

    command_received = Signal(str)
    finished = Signal()

    def __init__(self, bridge):
        super().__init__()

        self.listener = None
        self.running = True
        self.bridge = bridge

        # Indicates that JARVIS needs a follow-up
        # voice response.
        self.follow_up_requested = threading.Event()

    # ==================================================
    # REQUEST FOLLOW-UP
    # ==================================================

    def request_follow_up(self):
        """
        Requests one-time follow-up voice input.
        """

        self.follow_up_requested.set()

        if self.listener:
            self.listener.request_follow_up()

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

                # ==========================================
                # FOLLOW-UP INPUT
                # ==========================================

                if self.follow_up_requested.is_set():

                    self.follow_up_requested.clear()

                    self.bridge.set_state(JarvisState.LISTENING.value)
                    self.bridge.set_overlay_status("Listening...")

                    print("JARVIS: Waiting for your response...")

                    response = self.listener.listen_for_command()

                    # --------------------------------------
                    # NO FOLLOW-UP RESPONSE
                    # --------------------------------------

                    if not response:

                        print("JARVIS: No response received.")

                        self.bridge.set_state(JarvisState.IDLE.value)
                        self.bridge.set_state(JarvisState.SLEEPING.value)

                        continue

                    # --------------------------------------
                    # FOLLOW-UP RESPONSE RECEIVED
                    # --------------------------------------

                    self.bridge.send_transcript(response)
                    self.bridge.set_overlay_status(response)
                    self.command_received.emit(response)

                    continue

                # ==========================================
                # SLEEPING
                # ==========================================

                self.bridge.set_state(JarvisState.SLEEPING.value)
                self.bridge.set_overlay_status("Sleeping")

                awakened = self.listener.listen_for_wake_word()

                if not awakened:
                    continue

                # ==========================================
                # WAKE DETECTED
                # ==========================================

                self.bridge.wake_detected_event()

                # ==========================================
                # LISTENING FOR COMMAND
                # ==========================================

                self.bridge.set_state(JarvisState.LISTENING.value)
                self.bridge.set_overlay_status("Listening...")

                print("JARVIS: Waiting for your command...")

                command = self.listener.listen_for_command()

                # ==========================================
                # COMMAND TIMEOUT / EMPTY COMMAND
                # ==========================================

                if not command:

                    print("JARVIS: No command received.")

                    self.bridge.set_state(JarvisState.IDLE.value)
                    self.bridge.set_state(JarvisState.SLEEPING.value)
                    self.bridge.set_overlay_status("Sleeping")

                    self.listener.prepare_for_wake_word()

                    continue

                # ==========================================
                # COMMAND RECEIVED
                # ==========================================

                self.bridge.send_transcript(command)
                self.bridge.set_overlay_status(command)
                self.command_received.emit(command)

                # ==========================================
                # PREPARE FOR NEXT WAKE WORD
                # ==========================================

                self.listener.prepare_for_wake_word()

        finally:

            if self.listener:
                self.listener.close()

            self.finished.emit()

    # ==================================================
    # STOP
    # ==================================================

    def stop(self):
        """
        Stops the voice worker.
        """

        self.running = False

        self.follow_up_requested.set()

        if self.listener:
            self.listener.stop()
