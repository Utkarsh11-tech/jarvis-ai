from PySide6.QtCore import Signal

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

        # ==========================================
        # INPUT
        # ==========================================

        self.input = QLineEdit()

        self.input.setPlaceholderText(
            "How may I assist you?"
        )

        self.input.setFixedHeight(
            48
        )

        # Pressing Enter sends the message
        self.input.returnPressed.connect(
            self.send_message
        )

        # ==========================================
        # ARROW BUTTON
        # ==========================================

        self.send_button = QPushButton(
            "➤"
        )

        self.send_button.setFixedSize(
            58,
            48
        )

        self.send_button.clicked.connect(
            self.send_message
        )

        # ==========================================
        # LAYOUT
        # ==========================================

        self.input_layout = QHBoxLayout()

        self.input_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.input_layout.setSpacing(
            10
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

        # ==========================================
        # HUD STYLE
        # ==========================================

        self.setStyleSheet(
            """
            QLineEdit {
                background-color: #030A12;
                color: #DDEFFF;

                border: 1px solid #126486;
                border-radius: 12px;

                padding-left: 18px;
                padding-right: 18px;

                font-family:
                    "Orbitron",
                    "Eurostile",
                    "Arial";

                font-size: 13px;
                letter-spacing: 1px;
            }

            QLineEdit:hover {
                border: 1px solid #1788B5;
            }

            QLineEdit:focus {
                border: 1px solid #00D9FF;
            }

            QPushButton {
                background-color: #030A12;

                color: #00D9FF;

                border: 1px solid #126486;
                border-radius: 12px;

                font-size: 23px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #061522;

                color: #6FEAFF;

                border: 1px solid #00D9FF;
            }

            QPushButton:pressed {
                background-color: #0A2638;

                color: #FFFFFF;

                border: 1px solid #00D9FF;
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

        print(
            "CHAT INPUT:",
            repr(message)
        )

        # Send through signal
        self.message_sent.emit(
            message
        )

        # Clear input
        self.input.clear()

        # Keep keyboard focus
        self.input.setFocus()