from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLayout,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QLabel,
)

from body.app.widgets.chat_bubble import ChatBubble


class ConversationWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.messages = []
        self.notification_timer = QTimer(self)
        self.notification_timer.setSingleShot(True)
        self.notification_timer.timeout.connect(self.hide_notification)

        # ==========================================
        # MAIN LAYOUT
        # ==========================================

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(8)

        # ==========================================
        # TOOLBAR
        # ==========================================

        self.toolbar = QFrame()
        self.toolbar.setObjectName("conversationToolbar")

        self.toolbar_layout = QHBoxLayout(self.toolbar)
        self.toolbar_layout.setContentsMargins(10, 6, 10, 6)
        self.toolbar_layout.setSpacing(7)

        # Compact search icon. The actual search field stays hidden
        # until the user explicitly opens it.
        self.search_button = QPushButton("⌕")
        self.search_button.setObjectName("searchButton")
        self.search_button.setFixedSize(34, 30)
        self.search_button.setToolTip("Search conversation")
        self.search_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_button.clicked.connect(self.toggle_search)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search conversation...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.filter_messages)
        self.search_input.setVisible(False)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setFixedWidth(70)
        self.clear_button.clicked.connect(self.clear_conversation)

        self.toolbar_layout.addWidget(self.search_button)
        self.toolbar_layout.addWidget(self.search_input, 1)
        self.toolbar_layout.addWidget(self.clear_button)

        self.main_layout.addWidget(self.toolbar)

        # ==========================================
        # NOTIFICATION
        # ==========================================

        self.notification = QLabel()
        self.notification.setObjectName("conversationNotification")
        self.notification.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.notification.setVisible(False)
        self.main_layout.addWidget(self.notification)

        # ==========================================
        # CONVERSATION FRAME
        # ==========================================

        self.frame = QFrame()
        self.frame.setObjectName("conversationFrame")

        self.frame.setStyleSheet(
            """
            QFrame#conversationFrame {
                background-color: #02070D;
                border: 1px solid #126486;
                border-radius: 0px;
            }

            QFrame#conversationToolbar {
                background-color: #02070D;
                border: 1px solid #126486;
                border-radius: 8px;
            }

            QLineEdit {
                background-color: #030A12;
                color: #DDEFFF;
                border: 1px solid #126486;
                border-radius: 7px;
                padding: 7px 10px;
                font-size: 11px;
            }

            QLineEdit:focus {
                border: 1px solid #00D9FF;
            }

            QPushButton {
                background-color: #030A12;
                color: #8EDFFF;
                border: 1px solid #126486;
                border-radius: 7px;
                padding: 7px 10px;
                font-size: 10px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #061522;
                color: #FFFFFF;
                border: 1px solid #00D9FF;
            }

            QPushButton#searchButton {
                font-size: 19px;
                font-weight: 400;
                padding: 0px;
            }

            QLabel#conversationNotification {
                background-color: #061522;
                color: #8EDFFF;
                border: 1px solid #126486;
                border-radius: 7px;
                padding: 5px;
                font-size: 10px;
            }
            """
        )

        self.main_layout.addWidget(self.frame, 1)

        # ==========================================
        # FRAME LAYOUT
        # ==========================================

        self.frame_layout = QVBoxLayout(self.frame)
        self.frame_layout.setContentsMargins(0, 0, 0, 0)
        self.frame_layout.setSpacing(0)

        # ==========================================
        # SCROLL AREA
        # ==========================================

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
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

        self.frame_layout.addWidget(self.scroll_area)

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

        self.message_layout = QVBoxLayout(self.container)
        self.message_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.message_layout.setContentsMargins(24, 20, 24, 20)
        self.message_layout.setSpacing(14)
        self.message_layout.setSizeConstraint(
            QLayout.SizeConstraint.SetMinimumSize
        )

        self.scroll_area.setWidget(self.container)

    # ==================================================
    # ADD USER MESSAGE
    # ==================================================

    def add_user_message(self, message):
        self._add_message(message, True)

    # ==================================================
    # ADD JARVIS MESSAGE
    # ==================================================

    def add_jarvis_message(self, message):
        self._add_message(message, False)

        lowered = message.lower()

        error_terms = (
            "error",
            "unavailable",
            "couldn't",
            "could not",
            "cannot",
            "failed",
            "failure",
            "unable",
        )

        if any(term in lowered for term in error_terms):
            self.show_notification("✕ " + message)
        else:
            self.show_notification("✓ " + message)

    # ==================================================
    # ADD MESSAGE
    # ==================================================

    def _add_message(self, message, is_user):
        bubble = ChatBubble(message, is_user=is_user)

        self.message_layout.addWidget(
            bubble,
            alignment=(
                Qt.AlignmentFlag.AlignRight
                if is_user
                else Qt.AlignmentFlag.AlignLeft
            ),
        )

        self.messages.append((message, is_user, bubble))
        self._scroll_to_bottom_after_layout()

    # ==================================================
    # SEARCH TOGGLE
    # ==================================================

    def toggle_search(self):
        visible = self.search_input.isVisible()

        if visible:
            self.search_input.clear()
            self.search_input.setVisible(False)
            self.search_button.setToolTip("Search conversation")
            self.search_button.setFocus()
            return

        self.search_input.setVisible(True)
        self.search_input.setFocus()
        self.search_button.setToolTip("Close search")

    # ==================================================
    # SEARCH
    # ==================================================

    def filter_messages(self, query):
        query = query.strip().lower()

        for message, _is_user, bubble in self.messages:
            bubble.setVisible(
                not query or query in message.lower()
            )

    # ==================================================
    # CLEAR CONVERSATION
    # ==================================================

    def clear_conversation(self):
        for _message, _is_user, bubble in self.messages:
            bubble.deleteLater()

        self.messages.clear()
        self.search_input.clear()
        self.show_notification("Conversation cleared")

    # ==================================================
    # NOTIFICATION
    # ==================================================

    def show_notification(self, message):
        self.notification.setText(message)
        self.notification.setVisible(True)
        self.notification_timer.start(2200)

    def hide_notification(self):
        self.notification.setVisible(False)

    # ==================================================
    # SCROLL
    # ==================================================

    def _scroll_to_bottom_after_layout(self):
        QTimer.singleShot(0, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
