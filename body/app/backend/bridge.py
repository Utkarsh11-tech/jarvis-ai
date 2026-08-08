from PySide6.QtCore import QObject, Signal


class JarvisBridge(QObject):

    state_changed = Signal(str)
    response_received = Signal(str)

    def __init__(self):
        super().__init__()

    def set_state(self, state):
        self.state_changed.emit(state)

    def send_response(self, response):
        self.response_received.emit(response)