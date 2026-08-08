from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from body.app.widgets.chat_bubble import ChatBubble


class ConversationWidget(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

        # ---------- Scroll Area ----------
        self.setWidgetResizable(True)

        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # ---------- Container ----------
        self.container = QWidget()

        self.message_layout = QVBoxLayout(
            self.container
        )

        self.message_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        self.message_layout.setContentsMargins(
            20,
            15,
            20,
            15
        )

        self.message_layout.setSpacing(
            14
        )

        self.setWidget(
            self.container
        )

        # ---------- Styling ----------
        self.setStyleSheet(
            """
            QScrollArea {
                background-color: #0F0F13;
                border: none;
            }

            QScrollBar:vertical {
                width: 6px;
                background: transparent;
                margin: 5px 0px 5px 0px;
            }

            QScrollBar::handle:vertical {
                background: #252530;
                border-radius: 3px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background: #353545;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
            """
        )

    # ==================================================
    # ADD USER MESSAGE
    # ==================================================

    def add_user_message(self, message):
        bubble = ChatBubble(
            message,
            is_user=True
        )

        self.message_layout.addWidget(
            bubble,
            alignment=Qt.AlignmentFlag.AlignRight
        )

        self.scroll_to_bottom()

    # ==================================================
    # ADD JARVIS MESSAGE
    # ==================================================

    def add_jarvis_message(self, message):
        bubble = ChatBubble(
            message,
            is_user=False
        )

        self.message_layout.addWidget(
            bubble,
            alignment=Qt.AlignmentFlag.AlignLeft
        )

        self.scroll_to_bottom()

    # ==================================================
    # SCROLL TO BOTTOM
    # ==================================================

    def scroll_to_bottom(self):
        scrollbar = self.verticalScrollBar()

        scrollbar.setValue(
            scrollbar.maximum()
        )