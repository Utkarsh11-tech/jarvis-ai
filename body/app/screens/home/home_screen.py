from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from body.app.widgets.orb import OrbWidget, OrbState
from body.app.widgets.microphone import Microphone
from body.app.backend.bridge import JarvisBridge


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("JARVIS")
        self.resize(1000, 650)

        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main Layout
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # ---------- Header ----------
        self.header = QLabel("JARVIS")
        self.header.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        # ---------- Orb ----------
        self.orb = OrbWidget()

        # ---------- Microphone ----------
        self.microphone = Microphone()

        self.microphone.level_changed.connect(
            self.orb.set_audio_level
        )

        # ---------- Orb Click ----------
        self.orb.clicked.connect(
            self.toggle_listening
        )

        # ---------- Bridge ----------
        self.bridge = JarvisBridge()

        self.bridge.state_changed.connect(
            self.handle_state_change
        )

        # Initial state
        self.orb.set_state(
            OrbState.IDLE
        )

        # ---------- Status ----------
        self.status = QLabel(
            "Status : Waiting for command..."
        )
        self.status.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        # ---------- Chat ----------
        self.chat = QLabel(
            "Conversation Area"
        )
        self.chat.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        # ---------- Footer ----------
        self.footer = QLabel(
            "Version 0.1      |      Offline"
        )
        self.footer.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        # ---------- Add Widgets ----------
        self.main_layout.addWidget(
            self.header,
            1
        )

        self.main_layout.addWidget(
            self.orb,
            5
        )

        self.main_layout.addWidget(
            self.status,
            1
        )

        self.main_layout.addWidget(
            self.chat,
            3
        )

        self.main_layout.addWidget(
            self.footer,
            1
        )

    # ==================================================
    # TOGGLE LISTENING
    # ==================================================

    def toggle_listening(self):
        if self.orb.state == OrbState.IDLE:
            self.orb.set_state(
                OrbState.LISTENING
            )

            self.status.setText(
                "Status : Listening..."
            )

            self.microphone.start()

        elif self.orb.state == OrbState.LISTENING:
            self.microphone.stop()

            self.orb.set_state(
                OrbState.IDLE
            )

            self.status.setText(
                "Status : Waiting for command..."
            )

    # ==================================================
    # HANDLE JARVIS STATE
    # ==================================================

    def handle_state_change(self, state):
        try:
            orb_state = OrbState(
                state.lower()
            )

            self.orb.set_state(
                orb_state
            )

            self.status.setText(
                f"Status : {state.title()}"
            )

            # Start microphone only while listening
            if orb_state == OrbState.LISTENING:
                self.microphone.start()

            # Stop microphone for every other state
            else:
                self.microphone.stop()

        except ValueError:
            self.status.setText(
                f"Status : Unknown state ({state})"
            )