from PySide6.QtCore import QObject, Signal


class JarvisBridge(QObject):

    # Brain → Body
    state_changed = Signal(str)
    response_received = Signal(str)

    # Body → Brain
    command_requested = Signal(str)

    def __init__(self):
        super().__init__()

    # ================================================
    # BRAIN → BODY
    # ================================================

    def set_state(self, state):
        self.state_changed.emit(state)

    def send_response(self, response):
        self.response_received.emit(response)

    # ================================================
    # BODY → BRAIN
    # ================================================

    def send_command(self, command):
        self.command_requested.emit(command)