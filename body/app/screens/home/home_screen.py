from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from body.app.widgets.orb import OrbWidget, OrbState
from body.app.widgets.microphone import Microphone


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

        self.microphone = Microphone()

        self.microphone.level_changed.connect(
            self.orb.set_audio_level
        )

        # Orb starts in idle state
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