import math

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtWidgets import QApplication, QWidget


class JarvisOverlay(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # ==========================================
        # WINDOW
        # ==========================================

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_ShowWithoutActivating
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )

        # ==========================================
        # SIZE
        # ==========================================

        self.setFixedSize(430, 210)

        # ==========================================
        # STATE / STATUS
        # ==========================================

        self.audio_level = 0.0
        self.phase = 0.0
        self.status_text = "Listening..."

        # ==========================================
        # ANIMATION
        # ==========================================

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)

    # ==========================================
    # STATUS
    # ==========================================

    def set_status(self, status):
        """Updates the short status shown on the overlay."""

        status = str(status).strip()
        self.status_text = status or "Listening..."
        self.update()

    # ==========================================
    # SHOW OVERLAY
    # ==========================================

    def show_overlay(self):

        screen = QApplication.primaryScreen()

        if self.windowHandle() and self.windowHandle().screen():
            screen = self.windowHandle().screen()

        if screen is not None:

            geometry = screen.availableGeometry()

            x = (
                geometry.x()
                + (geometry.width() - self.width()) // 2
            )

            y = (
                geometry.y()
                + geometry.height()
                - self.height()
                - 80
            )

            self.move(x, y)

        self.show()
        self.raise_()
        self.timer.start(16)

    # ==========================================
    # HIDE OVERLAY
    # ==========================================

    def hide_overlay(self):

        self.timer.stop()
        self.hide()

    # ==========================================
    # AUDIO LEVEL
    # ==========================================

    def set_audio_level(self, level):

        self.audio_level = max(
            0.0,
            min(1.0, float(level))
        )

        self.update()

    # ==========================================
    # ANIMATION
    # ==========================================

    def update_animation(self):

        self.phase += 0.08

        if self.phase > math.pi * 2:
            self.phase = 0

        self.update()

    # ==========================================
    # PAINT
    # ==========================================

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        width = self.width()
        height = self.height()

        center_x = width // 2
        center_y = 82

        # ==========================================
        # SUBTLE GLOW
        # ==========================================

        glow_radius = (
            38
            + self.audio_level * 16
            + math.sin(self.phase) * 3
        )

        for radius, alpha in (
            (glow_radius + 24, 12),
            (glow_radius + 15, 20),
            (glow_radius + 8, 30),
        ):

            painter.setPen(
                QPen(
                    QColor(0, 210, 255, alpha),
                    2,
                )
            )

            painter.drawEllipse(
                int(center_x - radius),
                int(center_y - radius),
                int(radius * 2),
                int(radius * 2),
            )

        # ==========================================
        # WAVEFORM
        # ==========================================

        painter.setPen(
            QPen(
                QColor(0, 220, 255, 230),
                2,
            )
        )

        points = 80
        previous_x = 0
        previous_y = center_y

        for i in range(points):

            x = i * width / (points - 1)
            normalized = i / (points - 1)

            envelope = math.sin(normalized * math.pi)
            wave = math.sin(
                normalized * math.pi * 10 + self.phase
            )

            amplitude = 3 + self.audio_level * 22

            y = center_y + wave * amplitude * envelope

            if i > 0:
                painter.drawLine(
                    int(previous_x),
                    int(previous_y),
                    int(x),
                    int(y),
                )

            previous_x = x
            previous_y = y

        # ==========================================
        # CENTER CORE
        # ==========================================

        core_radius = 7 + self.audio_level * 6

        painter.setPen(
            QPen(
                QColor(0, 230, 255, 240),
                2,
            )
        )

        painter.drawEllipse(
            int(center_x - core_radius),
            int(center_y - core_radius),
            int(core_radius * 2),
            int(core_radius * 2),
        )

        # ==========================================
        # STATUS
        # ==========================================

        painter.setPen(
            QColor(190, 240, 255, 235)
        )

        status_font = QFont("Arial", 11)
        status_font.setBold(True)
        painter.setFont(status_font)

        painter.drawText(
            20,
            145,
            width - 40,
            28,
            Qt.AlignmentFlag.AlignCenter,
            self.status_text,
        )

        # ==========================================
        # LABEL
        # ==========================================

        painter.setPen(
            QColor(120, 200, 225, 180)
        )

        label_font = QFont("Arial", 9)
        label_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 3)
        painter.setFont(label_font)

        painter.drawText(
            0,
            height - 25,
            width,
            20,
            Qt.AlignmentFlag.AlignCenter,
            "J.A.R.V.I.S",
        )
