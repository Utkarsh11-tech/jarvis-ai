from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor,
    QPainter,
    QRadialGradient,
)
from PySide6.QtWidgets import QWidget


class OrbWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumSize(300, 300)

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        painter.setPen(Qt.PenStyle.NoPen)

        # ---------- Center ----------
        center_x = self.width() // 2
        center_y = self.height() // 2

        # ---------- Responsive Size ----------
        radius = min(
            self.width(),
            self.height()
        ) // 4

        # ==================================================
        # OUTER GLOW
        # ==================================================

        glow_radius = int(radius * 1.45)

        gradient = QRadialGradient(
            center_x,
            center_y,
            glow_radius
        )

        gradient.setColorAt(
            0.0,
            QColor(0, 217, 255, 80)
        )

        gradient.setColorAt(
            0.45,
            QColor(0, 217, 255, 30)
        )

        gradient.setColorAt(
            1.0,
            QColor(0, 217, 255, 0)
        )

        painter.setBrush(gradient)

        painter.drawEllipse(
            center_x - glow_radius,
            center_y - glow_radius,
            glow_radius * 2,
            glow_radius * 2
        )

        # ==================================================
        # OUTER ORB
        # ==================================================

        painter.setBrush(
            QColor("#00D9FF")
        )

        painter.drawEllipse(
            center_x - radius,
            center_y - radius,
            radius * 2,
            radius * 2
        )

        # ==================================================
        # INNER BODY
        # ==================================================

        inner_radius = int(radius * 0.72)

        painter.setBrush(
            QColor("#0F0F13")
        )

        painter.drawEllipse(
            center_x - inner_radius,
            center_y - inner_radius,
            inner_radius * 2,
            inner_radius * 2
        )

        # ==================================================
        # CORE GLOW
        # ==================================================

        core_radius = int(radius * 0.25)

        core_gradient = QRadialGradient(
            center_x,
            center_y,
            core_radius
        )

        core_gradient.setColorAt(
            0.0,
            QColor(255, 255, 255, 255)
        )

        core_gradient.setColorAt(
            0.35,
            QColor(0, 217, 255, 255)
        )

        core_gradient.setColorAt(
            1.0,
            QColor(0, 217, 255, 0)
        )

        painter.setBrush(core_gradient)

        painter.drawEllipse(
            center_x - core_radius,
            center_y - core_radius,
            core_radius * 2,
            core_radius * 2
        )