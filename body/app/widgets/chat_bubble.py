from PySide6.QtCore import Qt, QTimer

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
        super().__init__(
            parent
        )

        self.message = message
        self.is_user = is_user

        # ==================================================
        # THEME
        # ==================================================

        self.theme = "dark"

        # ==================================================
        # MAIN LAYOUT
        # ==================================================

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

        # ==================================================
        # HEADER
        # ==================================================

        self.header = QLabel(
            "YOU"
            if self.is_user
            else "JARVIS"
        )

        self.header.setAlignment(
            Qt.AlignmentFlag.AlignLeft
        )

        # ==================================================
        # MESSAGE
        # ==================================================

        self.label = QLabel(
            message
        )

        self.label.setWordWrap(
            True
        )

        self.label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        self.label.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )

        # ==================================================
        # ADD WIDGETS
        # ==================================================

        self.message_layout.addWidget(
            self.header
        )

        self.message_layout.addWidget(
            self.label
        )

        # ==================================================
        # ALIGNMENT
        # ==================================================

        if self.is_user:

            self.message_layout.setAlignment(
                Qt.AlignmentFlag.AlignRight
            )

        else:

            self.message_layout.setAlignment(
                Qt.AlignmentFlag.AlignLeft
            )

        # ==================================================
        # BUBBLE SIZE
        # ==================================================

        bubble_width = 500

        margins = (
            self.message_layout.contentsMargins()
        )

        text_width = (
            bubble_width
            - margins.left()
            - margins.right()
            - 2
        )

        self.label.setFixedWidth(
            text_width
        )

        self._text_width = (
            text_width
        )

        self.setFixedWidth(
            bubble_width
        )

        # ==================================================
        # APPLY INITIAL THEME
        # ==================================================

        self.apply_theme(
            "dark"
        )

        # ==================================================
        # INITIAL TEXT HEIGHT
        # ==================================================

        self._update_text_height()

        QTimer.singleShot(
            0,
            self._update_text_height
        )

    # ==================================================
    # THEME
    # ==================================================

    def apply_theme(
        self,
        theme
    ):

        self.theme = str(
            theme
        ).lower()

        if self.theme == "light":

            # ==================================================
            # LIGHT BUBBLE
            # ==================================================

            if self.is_user:

                background = "#D7F3FA"
                border = "#42A9C4"

            else:

                background = "#F4FCFE"
                border = "#72B8CA"

            self.setStyleSheet(
                f"""
                QFrame {{
                    background-color: {background};
                    border: 1px solid {border};
                    border-radius: 14px;
                }}

                QLabel {{
                    background: transparent;
                    border: none;
                }}
                """
            )

            self.header.setStyleSheet(
                """
                QLabel {
                    color: #007B9E;
                    background: transparent;
                    border: none;
                    font-size: 11px;
                    font-weight: bold;
                }
                """
            )

            self.label.setStyleSheet(
                """
                QLabel {
                    color: #08202C;
                    background: transparent;
                    border: none;
                    font-size: 14px;
                }
                """
            )

        else:

            # ==================================================
            # DARK BUBBLE
            # ==================================================

            if self.is_user:

                background = "#15151C"
                border = "#252530"

            else:

                background = "#15151C"
                border = "#252530"

            self.setStyleSheet(
                f"""
                QFrame {{
                    background-color: {background};
                    border: 1px solid {border};
                    border-radius: 14px;
                }}

                QLabel {{
                    background: transparent;
                    border: none;
                }}
                """
            )

            self.header.setStyleSheet(
                """
                QLabel {
                    color: #00D9FF;
                    background: transparent;
                    border: none;
                    font-size: 11px;
                    font-weight: bold;
                }
                """
            )

            self.label.setStyleSheet(
                """
                QLabel {
                    color: #F2F2F2;
                    background: transparent;
                    border: none;
                    font-size: 14px;
                }
                """
            )

        self.update()

    # ==================================================
    # UPDATE TEXT HEIGHT
    # ==================================================

    def _update_text_height(
        self
    ):

        self.label.setFixedHeight(
            self.label.heightForWidth(
                self._text_width
            )
        )

        self.message_layout.invalidate()

        self.updateGeometry()