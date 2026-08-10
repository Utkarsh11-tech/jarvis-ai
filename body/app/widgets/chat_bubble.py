from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QFrame,
)


class ChatBubble(QFrame):
    def __init__(
        self,
        message,
        is_user=False,
        parent=None
    ):
        super().__init__(parent)

        self.message = message
        self.is_user = is_user

        # ---------- Main Layout ----------
        self.message_layout = QVBoxLayout()

        self.message_layout.setContentsMargins(
            14,
            10,
            14,
            10
        )

        self.message_layout.setSpacing(5)

        self.setLayout(
            self.message_layout
        )

        # ---------- Header ----------
        self.header = QLabel(
            "YOU" if self.is_user else "JARVIS"
        )

        self.header.setAlignment(
            Qt.AlignmentFlag.AlignLeft
        )

        # ---------- Message ----------
        self.label = QLabel(
            message
        )

        self.label.setWordWrap(True)

        self.label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        self.label.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Minimum,
        )

        self.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Preferred,
        )

        # ---------- Add Widgets ----------
        self.message_layout.addWidget(
            self.header
        )

        self.message_layout.addWidget(
            self.label
        )

        # ---------- Alignment ----------
        if self.is_user:
            self.message_layout.setAlignment(
                Qt.AlignmentFlag.AlignRight
            )

        else:
            self.message_layout.setAlignment(
                Qt.AlignmentFlag.AlignLeft
            )

        # ---------- Styling ----------
        self.setStyleSheet(
            """
            QFrame {
                background-color: #15151C;
                border: 1px solid #252530;
                border-radius: 14px;
            }

            QLabel {
                color: white;
                background: transparent;
                border: none;
            }
            """
        )

        # ---------- Header Styling ----------
        self.header.setStyleSheet(
            """
            QLabel {
                color: #00D9FF;
                font-size: 11px;
                font-weight: bold;
            }
            """
        )

        # ---------- Message Styling ----------
        self.label.setStyleSheet(
            """
            QLabel {
                color: #F2F2F2;
                font-size: 14px;
            }
            """
        )

        # ---------- Bubble Width ----------
        self.setMaximumWidth(500)
