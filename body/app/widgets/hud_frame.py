from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QPainter,
    QPen,
    QColor,
)
from PySide6.QtWidgets import QWidget


# ============================================================
# HUD FRAME
# ============================================================


class HUDFrame(QWidget):

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        self.theme = "dark"

        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )

    def set_theme(
        self,
        theme,
    ):

        self.theme = theme.lower()

        self.update()

    def paintEvent(
        self,
        event,
    ):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        width = self.width()
        height = self.height()

        if self.theme == "light":

            frame_color = QColor(
                0,
                120,
                160,
                100,
            )

            marker_color = QColor(
                0,
                150,
                190,
                80,
            )

        else:

            frame_color = QColor(
                0,
                150,
                210,
                75,
            )

            marker_color = QColor(
                0,
                217,
                255,
                45,
            )

        painter.setPen(
            QPen(
                frame_color,
                1,
            )
        )

        margin = 8
        corner = 28

        # TOP LEFT

        painter.drawLine(
            margin,
            margin,
            margin + corner,
            margin,
        )

        painter.drawLine(
            margin,
            margin,
            margin,
            margin + corner,
        )

        # TOP RIGHT

        painter.drawLine(
            width - margin - corner,
            margin,
            width - margin,
            margin,
        )

        painter.drawLine(
            width - margin,
            margin,
            width - margin,
            margin + corner,
        )

        # BOTTOM LEFT

        painter.drawLine(
            margin,
            height - margin,
            margin + corner,
            height - margin,
        )

        painter.drawLine(
            margin,
            height - margin - corner,
            margin,
            height - margin,
        )

        # BOTTOM RIGHT

        painter.drawLine(
            width - margin - corner,
            height - margin,
            width - margin,
            height - margin,
        )

        painter.drawLine(
            width - margin,
            height - margin - corner,
            width - margin,
            height - margin,
        )

        # ========================================================
        # SIDE MARKERS
        # ========================================================

        painter.setPen(
            QPen(
                marker_color,
                1,
            )
        )

        center_y = height // 2

        painter.drawLine(
            margin,
            center_y - 40,
            margin,
            center_y + 40,
        )

        painter.drawLine(
            width - margin,
            center_y - 40,
            width - margin,
            center_y + 40,
        )

        # ========================================================
        # HUD TICKS
        # ========================================================

        for x in range(
            80,
            width - 80,
            80,
        ):

            painter.drawLine(
                x,
                margin,
                x,
                margin + 5,
            )

            painter.drawLine(
                x,
                height - margin - 5,
                x,
                height - margin,
            )
