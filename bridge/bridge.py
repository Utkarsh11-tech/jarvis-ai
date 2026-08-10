from PySide6.QtCore import QObject, Signal


class JarvisBridge(QObject):

    # ==================================================
    # BRAIN → BODY
    # ==================================================

    state_changed = Signal(str)
    response_received = Signal(str)

    # Wake word was detected
    wake_detected = Signal()

    # Requests that require user interaction in the GUI.
    profile_selection_requested = Signal(list)

    # Requests one-time voice input from VoiceWorker.
    voice_input_requested = Signal()

    # ==================================================
    # BODY → BRAIN
    # ==================================================

    command_requested = Signal(str)

    # Result of a GUI profile selection.
    profile_selected = Signal(str)

    def __init__(self):
        super().__init__()

    # ==================================================
    # BRAIN → BODY
    # ==================================================

    def set_state(self, state):
        self.state_changed.emit(state)

    def send_response(self, response):
        self.response_received.emit(response)

    def wake_detected_event(self):
        self.wake_detected.emit()

    def request_profile_selection(self, profiles):
        self.profile_selection_requested.emit(profiles)

    def request_voice_input(self):
        self.voice_input_requested.emit()

    # ==================================================
    # BODY → BRAIN
    # ==================================================

    def send_command(self, command):
        self.command_requested.emit(command)

    def send_profile_selection(self, profile):
        self.profile_selected.emit(profile)
