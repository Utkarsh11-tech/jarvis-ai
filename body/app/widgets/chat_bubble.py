from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QFrame,
    QSizePolicy,
)


class ChatBubble(QFrame):

    def __init__(
        self,
        message,
        is_user=False,
        parent=None
    ):
        super().__init__(parent)

        self.message = str(message)
        self.is_user = is_user

        # ==========================================
        # MAIN LAYOUT
        # ==========================================

        self.message_layout = QVBoxLayout()

        self.message_layout.setContentsMargins(
            14,
            10,
            14,
            10
        )

        self.message_layout.setSpacing(
            5
        )

        self.setLayout(
            self.message_layout
        )

        # ==========================================
        # HEADER
        # ==========================================

        self.header = QLabel(
            "YOU" if self.is_user else "JARVIS"
        )

        self.header.setAlignment(
            Qt.AlignmentFlag.AlignLeft
        )

        # ==========================================
        # MESSAGE
        # ==========================================

        self.label = QLabel(
            self.message
        )

        # IMPORTANT:
        # Allow the complete message to wrap.
        self.label.setWordWrap(True)

        self.label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        self.label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )

        # Allow the label to calculate its
        # required height from the complete text.
        self.label.setMinimumHeight(
            0
        )

        # ==========================================
        # ADD WIDGETS
        # ==========================================

        self.message_layout.addWidget(
            self.header
        )

        self.message_layout.addWidget(
            self.label
        )

        # ==========================================
        # ALIGNMENT
        # ==========================================

        if self.is_user:

            self.message_layout.setAlignment(
                Qt.AlignmentFlag.AlignRight
            )

        else:

            self.message_layout.setAlignment(
                Qt.AlignmentFlag.AlignLeft
            )

        # ==========================================
        # BUBBLE SIZE
        # ==========================================

        self.setMaximumWidth(
            500
        )

        self.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Minimum
        )

        # ==========================================
        # STYLING
        # ==========================================

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

        # ==========================================
        # HEADER STYLING
        # ==========================================

        self.header.setStyleSheet(
            """
            QLabel {
                color: #00D9FF;
                font-size: 11px;
                font-weight: bold;
            }
            """
        )

        # ==========================================
        # MESSAGE STYLING
        # ==========================================

        self.label.setStyleSheet(
            """
            QLabel {
                color: #F2F2F2;
                font-size: 14px;
            }
            """
        )