from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)

from body.app.widgets.conversation import ConversationWidget
from body.app.widgets.chat_input import ChatInput


class ChatScreen(QWidget):

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        self.theme = "dark"

        # ==================================================
        # MAIN LAYOUT
        # ==================================================

        self.main_layout = QVBoxLayout(self)

        self.main_layout.setContentsMargins(
            32,
            24,
            32,
            24,
        )

        self.main_layout.setSpacing(
            12
        )

        # ==================================================
        # HEADER
        # ==================================================

        self.header = QLabel(
            "CONVERSATION"
        )

        self.header.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.main_layout.addWidget(
            self.header
        )

        # ==================================================
        # SUBTITLE
        # ==================================================

        self.subtitle = QLabel(
            "J.A.R.V.I.S COMMAND HISTORY"
        )

        self.subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.main_layout.addWidget(
            self.subtitle
        )

        # ==================================================
        # CONVERSATION
        # ==================================================

        self.conversation = ConversationWidget()

        self.main_layout.addWidget(
            self.conversation,
            1,
        )

        # ==================================================
        # INPUT
        # ==================================================

        self.chat_input = ChatInput()

        self.main_layout.addWidget(
            self.chat_input
        )

        # ==================================================
        # INITIAL THEME
        # ==================================================

        self.apply_theme(
            "dark"
        )

    # ==================================================
    # THEME
    # ==================================================

    def apply_theme(
        self,
        theme,
    ):

        self.theme = theme.lower()

        self.conversation.apply_theme(
            self.theme
        )

        self.chat_input.apply_theme(
            self.theme
        )

        if self.theme == "light":

            self.setStyleSheet(
                """
                QWidget {
                    background: transparent;
                }

                QLabel {
                    background: transparent;
                    color: #08202C;
                }
                """
            )

            self.header.setStyleSheet(
                """
                QLabel {
                    color: #08202C;
                    font-family:
                        "Orbitron",
                        "Eurostile",
                        "Arial";
                    font-size: 25px;
                    font-weight: 700;
                    letter-spacing: 6px;
                }
                """
            )

            self.subtitle.setStyleSheet(
                """
                QLabel {
                    color: #26728A;
                    font-family:
                        "Orbitron",
                        "Eurostile",
                        "Arial";
                    font-size: 10px;
                    font-weight: 600;
                    letter-spacing: 3px;
                }
                """
            )

        else:

            self.setStyleSheet(
                """
                QWidget {
                    background: transparent;
                }

                QLabel {
                    background: transparent;
                    color: #DDEFFF;
                }
                """
            )

            self.header.setStyleSheet(
                """
                QLabel {
                    color: #DDEFFF;
                    font-family:
                        "Orbitron",
                        "Eurostile",
                        "Arial";
                    font-size: 25px;
                    font-weight: 700;
                    letter-spacing: 6px;
                }
                """
            )

            self.subtitle.setStyleSheet(
                """
                QLabel {
                    color: #5C91B5;
                    font-family:
                        "Orbitron",
                        "Eurostile",
                        "Arial";
                    font-size: 10px;
                    font-weight: 600;
                    letter-spacing: 3px;
                }
                """
            )