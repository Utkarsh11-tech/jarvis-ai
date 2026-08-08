from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush, QPainter
from PySide6.QtWidgets import QWidget


class OrbWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumSize(300, 300)

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QBrush(QColor("#00D9FF")))

        painter.setPen(Qt.PenStyle.NoPen)

        painter.drawEllipse(50, 50, 200, 200)