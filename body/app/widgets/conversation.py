from PySide6.QtCore import Qt, QTimer

from PySide6.QtWidgets import (
    QFrame,
    QLayout,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from body.app.widgets.chat_bubble import ChatBubble


class ConversationWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # ==========================================
        # MAIN LAYOUT
        # ==========================================

        self.main_layout = QVBoxLayout(
            self
        )

        self.main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.main_layout.setSpacing(
            0
        )

        # ==========================================
        # CONVERSATION FRAME
        # ==========================================

        self.frame = QFrame()

        self.frame.setObjectName(
            "conversationFrame"
        )

        self.frame.setStyleSheet(
            """
            QFrame#conversationFrame {
                background-color: #02070D;
                border: 1px solid #126486;
                border-radius: 0px;
            }
            """
        )

        self.main_layout.addWidget(
            self.frame
        )

        # ==========================================
        # FRAME LAYOUT
        # ==========================================

        self.frame_layout = QVBoxLayout(
            self.frame
        )

        self.frame_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.frame_layout.setSpacing(
            0
        )

        # ==========================================
        # SCROLL AREA
        # ==========================================

        self.scroll_area = QScrollArea()

        self.scroll_area.setWidgetResizable(
            True
        )

        self.scroll_area.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.scroll_area.setStyleSheet(
            """
            QScrollArea {
                background-color: #02070D;
                border: none;
            }

            QScrollBar:vertical {
                width: 6px;
                background: transparent;
                margin: 8px 3px 8px 3px;
            }

            QScrollBar::handle:vertical {
                background: #126486;
                border-radius: 3px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background: #00D9FF;
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

        self.frame_layout.addWidget(
            self.scroll_area
        )

        # ==========================================
        # MESSAGE CONTAINER
        # ==========================================

        self.container = QWidget()

        self.container.setStyleSheet(
            """
            QWidget {
                background-color: #02070D;
                border: none;
            }
            """
        )

        self.message_layout = QVBoxLayout(
            self.container
        )

        self.message_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        self.message_layout.setContentsMargins(
            24,
            20,
            24,
            20
        )

        self.message_layout.setSpacing(
            14
        )

        # Let the scroll area's content grow to the complete height of
        # wrapped chat bubbles instead of keeping only the viewport height.
        self.message_layout.setSizeConstraint(
            QLayout.SizeConstraint.SetMinimumSize
        )

        self.scroll_area.setWidget(
            self.container
        )

    # ==================================================
    # ADD USER MESSAGE
    # ==================================================

    def add_user_message(
        self,
        message
    ):

        bubble = ChatBubble(
            message,
            is_user=True
        )

        self.message_layout.addWidget(
            bubble,
            alignment=Qt.AlignmentFlag.AlignRight
        )

        self._scroll_to_bottom_after_layout()

    # ==================================================
    # ADD JARVIS MESSAGE
    # ==================================================

    def add_jarvis_message(
        self,
        message
    ):

        bubble = ChatBubble(
            message,
            is_user=False
        )

        self.message_layout.addWidget(
            bubble,
            alignment=Qt.AlignmentFlag.AlignLeft
        )

        self._scroll_to_bottom_after_layout()

    def _scroll_to_bottom_after_layout(self):
        """Scroll after Qt has calculated the new bubble's wrapped height."""

        QTimer.singleShot(
            0,
            self.scroll_to_bottom,
        )

    # ==================================================
    # SCROLL TO BOTTOM
    # ==================================================

    def scroll_to_bottom(
        self
    ):

        scrollbar = (
            self.scroll_area.verticalScrollBar()
        )

        scrollbar.setValue(
            scrollbar.maximum()
        )
