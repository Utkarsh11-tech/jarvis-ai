from PySide6.QtCore import Qt, Signal

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)


class ChatInput(QWidget):

    # Emitted when the user sends a message
    message_sent = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # ---------- Input ----------
        self.input = QLineEdit()

        self.input.setPlaceholderText(
            "How may I assist you?"
        )

        self.input.setFixedHeight(
            42
        )

        # Pressing Enter sends the message
        self.input.returnPressed.connect(
            self.send_message
        )

        # ---------- Send Button ----------
        self.send_button = QPushButton(
            "➤"
        )

        self.send_button.setFixedSize(
            50,
            42
        )

        self.send_button.clicked.connect(
            self.send_message
        )

        # ---------- Layout ----------
        self.input_layout = QHBoxLayout()

        self.input_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.input_layout.setSpacing(
            8
        )

        self.setLayout(
            self.input_layout
        )

        self.input_layout.addWidget(
            self.input
        )

        self.input_layout.addWidget(
            self.send_button
        )

        # ---------- Styling ----------
        self.setStyleSheet(
            """
            QLineEdit {
                background-color: #15151C;
                color: #F2F2F2;
                border: 1px solid #252530;
                border-radius: 12px;
                padding: 10px 14px;
                font-size: 14px;
            }

            QLineEdit:focus {
                border: 1px solid #00D9FF;
            }

            QPushButton {
                background-color: #15151C;
                color: #00D9FF;
                border: 1px solid #252530;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1C1C25;
                border: 1px solid #00D9FF;
            }

            QPushButton:pressed {
                background-color: #252530;
            }
            """
        )

    # ==================================================
    # SEND MESSAGE
    # ==================================================

    def send_message(self):

        message = self.input.text().strip()

        # Don't send empty messages
        if not message:
            return

        # Send message through signal
        self.message_sent.emit(
            message
        )

        # Clear input
        self.input.clear()

        # Keep keyboard focus
        self.input.setFocus()