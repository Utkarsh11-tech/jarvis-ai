import math
from enum import Enum

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import QWidget


class OrbState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    EXECUTING = "executing"
    ERROR = "error"
    SUCCESS = "success"


class OrbWidget(QWidget):
    clicked = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumSize(300, 300)

        # ==================================================
        # JARVIS STATE
        # ==================================================

        self.state = OrbState.IDLE

        # ==================================================
        # ANIMATION
        # ==================================================

        self.rotation = 0
        self.pulse = 0

        # ==================================================
        # AUDIO REACTIVITY
        # ==================================================

        # Current displayed audio level
        self.audio_level = 0.0

        # Target audio level received from microphone / TTS
        self.target_audio_level = 0.0

        # ==================================================
        # ANIMATION TIMER
        # ==================================================

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    # ======================================================
    # ANIMATION
    # ======================================================

    def animate(self):
        # Rotating HUD elements
        self.rotation = (
            self.rotation + 0.8
        ) % 360

        # State-based pulse speed
        if self.state == OrbState.LISTENING:
            self.pulse += 0.12

        elif self.state == OrbState.SPEAKING:
            self.pulse += 0.18

        elif self.state == OrbState.THINKING:
            self.pulse += 0.08

        elif self.state == OrbState.EXECUTING:
            self.pulse += 0.12

        else:
            self.pulse += 0.04

        # Smooth audio reaction
        self.audio_level += (
            self.target_audio_level
            - self.audio_level
        ) * 0.18

        # Redraw
        self.update()

    # ======================================================
    # STATE
    # ======================================================

    def set_state(self, state):
        self.state = state
        self.update()

    # ======================================================
    # AUDIO LEVEL
    # ======================================================

    def set_audio_level(self, level):
        """
        Receives an audio level between 0.0 and 1.0.

        0.0 = silence
        1.0 = maximum detected volume
        """

        level = max(
            0.0,
            min(1.0, float(level))
        )

        self.target_audio_level = level

    # ======================================================
    # PAINT EVENT
    # ======================================================

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        # ==================================================
        # CENTER
        # ==================================================

        center_x = self.width() / 2
        center_y = self.height() / 2

        center = (
            center_x,
            center_y
        )

        # ==================================================
        # RESPONSIVE SIZE
        # ==================================================

        base_radius = min(
            self.width(),
            self.height()
        ) * 0.38

        # Normal breathing
        breathing = math.sin(self.pulse) * 0.025

        # Stronger reaction while listening
        if self.state == OrbState.LISTENING:
            breathing = math.sin(self.pulse) * 0.015

        # Voice-driven expansion
        voice_reaction = self.audio_level * 0.15

        #Final radius
        radius = base_radius * (
            1
            + breathing
            + voice_reaction
        )

        # ==================================================
        # STATE-BASED GLOW
        # ==================================================

        if self.state == OrbState.LISTENING:
            glow_strength = 90

        elif self.state == OrbState.THINKING:
            glow_strength = 70

        elif self.state == OrbState.SPEAKING:
            glow_strength = 100

        elif self.state == OrbState.ERROR:
            glow_strength = 100

        elif self.state == OrbState.SUCCESS:
            glow_strength = 80

        else:
            glow_strength = 45

        # Additional glow from voice
        glow_strength += int(
            self.audio_level * 80
        )

        glow_strength = min(
            glow_strength,
            255
        )

        # ==================================================
        # OUTER GLOW
        # ==================================================

        glow_radius = radius * 1.18

        glow = QRadialGradient(
            center_x,
            center_y,
            glow_radius
        )

        glow.setColorAt(
            0.0,
            QColor(
                0,
                217,
                255,
                glow_strength
            )
        )

        glow.setColorAt(
            0.45,
            QColor(
                0,
                217,
                255,
                glow_strength // 2
            )
        )

        glow.setColorAt(
            1.0,
            QColor(
                0,
                217,
                255,
                0
            )
        )

        painter.setBrush(glow)

        painter.drawEllipse(
            int(center_x - glow_radius),
            int(center_y - glow_radius),
            int(glow_radius * 2),
            int(glow_radius * 2)
        )

        # ==================================================
        # OUTER THIN RINGS
        # ==================================================

        self.draw_circle(
            painter,
            center,
            radius * 0.98,
            QColor(0, 217, 255, 110),
            1
        )

        self.draw_circle(
            painter,
            center,
            radius * 0.91,
            QColor(0, 217, 255, 45),
            1
        )

        self.draw_circle(
            painter,
            center,
            radius * 0.84,
            QColor(0, 217, 255, 75),
            1
        )

        # ==================================================
        # ROTATING OUTER ARCS
        # ==================================================

        self.draw_arc(
            painter,
            center,
            radius * 0.94,
            self.rotation,
            70,
            3,
            QColor(0, 217, 255, 210)
        )

        self.draw_arc(
            painter,
            center,
            radius * 0.94,
            self.rotation + 150,
            45,
            2,
            QColor(0, 217, 255, 130)
        )

        self.draw_arc(
            painter,
            center,
            radius * 0.94,
            self.rotation + 270,
            80,
            2,
            QColor(0, 217, 255, 100)
        )

        # ==================================================
        # SECOND ROTATING RING
        # ==================================================

        self.draw_arc(
            painter,
            center,
            radius * 0.76,
            -self.rotation * 1.4,
            120,
            3,
            QColor(0, 217, 255, 170)
        )

        self.draw_arc(
            painter,
            center,
            radius * 0.76,
            -self.rotation * 1.4 + 180,
            75,
            2,
            QColor(0, 217, 255, 100)
        )

        # ==================================================
        # DOT RING
        # ==================================================

        dot_radius = radius * 0.68

        for i in range(36):
            angle = math.radians(
                i * 10
                + self.rotation * 0.5
            )

            x = (
                center_x
                + math.cos(angle)
                * dot_radius
            )

            y = (
                center_y
                + math.sin(angle)
                * dot_radius
            )

            dot_size = 3

            if i % 6 == 0:
                dot_size = 5

            # Voice makes dots brighter
            dot_alpha = min(
                255,
                150
                + int(self.audio_level * 105)
            )

            painter.setBrush(
                QColor(
                    0,
                    217,
                    255,
                    dot_alpha
                )
            )

            painter.drawEllipse(
                int(x - dot_size / 2),
                int(y - dot_size / 2),
                dot_size,
                dot_size
            )

        # ==================================================
        # SEGMENTED RING
        # ==================================================

        segment_radius = radius * 0.58

        for i in range(24):
            start_angle = (
                i * 15
                + self.rotation * 0.35
            )

            if i % 2 == 0:
                color = QColor(
                    0,
                    217,
                    255,
                    220
                )
                width = 5

            else:
                color = QColor(
                    0,
                    217,
                    255,
                    65
                )
                width = 3

            self.draw_arc(
                painter,
                center,
                segment_radius,
                start_angle,
                9,
                width,
                color
            )

        # ==================================================
        # INNER RINGS
        # ==================================================

        self.draw_circle(
            painter,
            center,
            radius * 0.49,
            QColor(0, 217, 255, 140),
            2
        )

        self.draw_circle(
            painter,
            center,
            radius * 0.42,
            QColor(0, 217, 255, 80),
            1
        )

        # ==================================================
        # CORE OUTER GLOW
        # ==================================================

        core_radius = radius * 0.31

        core_glow = QRadialGradient(
            center_x,
            center_y,
            core_radius * 1.5
        )

        core_glow.setColorAt(
            0.0,
            QColor(
                255,
                255,
                255,
                220
            )
        )

        core_glow.setColorAt(
            0.25,
            QColor(
                0,
                217,
                255,
                180
            )
        )

        core_glow.setColorAt(
            0.65,
            QColor(
                0,
                217,
                255,
                45
            )
        )

        core_glow.setColorAt(
            1.0,
            QColor(
                0,
                217,
                255,
                0
            )
        )

        painter.setBrush(core_glow)

        painter.drawEllipse(
            int(
                center_x
                - core_radius * 1.5
            ),
            int(
                center_y
                - core_radius * 1.5
            ),
            int(core_radius * 3),
            int(core_radius * 3)
        )

        # ==================================================
        # CORE
        # ==================================================

        core = QRadialGradient(
            center_x,
            center_y,
            core_radius
        )

        core.setColorAt(
            0.0,
            QColor(
                255,
                255,
                255,
                255
            )
        )

        core.setColorAt(
            0.25,
            QColor(
                0,
                230,
                255,
                255
            )
        )

        core.setColorAt(
            0.75,
            QColor(
                0,
                100,
                150,
                255
            )
        )

        core.setColorAt(
            1.0,
            QColor(
                0,
                30,
                50,
                255
            )
        )

        painter.setBrush(core)

        painter.drawEllipse(
            int(
                center_x - core_radius
            ),
            int(
                center_y - core_radius
            ),
            int(core_radius * 2),
            int(core_radius * 2)
        )

        # ==================================================
        # CORE HEXAGON TEXTURE
        # ==================================================

        painter.setBrush(
            Qt.BrushStyle.NoBrush
        )

        painter.setPen(
            QPen(
                QColor(
                    0,
                    217,
                    255,
                    90
                ),
                1
            )
        )

        hex_radius = core_radius * 0.72

        for ring in range(1, 4):
            current_radius = (
                hex_radius
                * ring
                / 3
            )

            self.draw_hex_ring(
                painter,
                center_x,
                center_y,
                current_radius
            )

        # ==================================================
        # CENTER POINT
        # ==================================================

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        center_glow = QRadialGradient(
            center_x,
            center_y,
            core_radius * 0.35
        )

        center_glow.setColorAt(
            0.0,
            QColor(
                255,
                255,
                255,
                255
            )
        )

        center_glow.setColorAt(
            0.5,
            QColor(
                0,
                240,
                255,
                240
            )
        )

        center_glow.setColorAt(
            1.0,
            QColor(
                0,
                217,
                255,
                0
            )
        )

        painter.setBrush(center_glow)

        center_point = (
            core_radius * 0.22
        )

        painter.drawEllipse(
            int(
                center_x - center_point
            ),
            int(
                center_y - center_point
            ),
            int(center_point * 2),
            int(center_point * 2)
        )

    # ======================================================
    # DRAW CIRCLE
    # ======================================================

    def draw_circle(
        self,
        painter,
        center,
        radius,
        color,
        width
    ):
        center_x, center_y = center

        painter.setBrush(
            Qt.BrushStyle.NoBrush
        )

        painter.setPen(
            QPen(
                color,
                width
            )
        )

        painter.drawEllipse(
            int(center_x - radius),
            int(center_y - radius),
            int(radius * 2),
            int(radius * 2)
        )

    # ======================================================
    # DRAW ARC
    # ======================================================

    def draw_arc(
        self,
        painter,
        center,
        radius,
        start_angle,
        span_angle,
        width,
        color
    ):
        center_x, center_y = center

        painter.setBrush(
            Qt.BrushStyle.NoBrush
        )

        painter.setPen(
            QPen(
                color,
                width
            )
        )

        painter.drawArc(
            int(center_x - radius),
            int(center_y - radius),
            int(radius * 2),
            int(radius * 2),
            int(-start_angle * 16),
            int(-span_angle * 16)
        )

    # ======================================================
    # DRAW HEXAGON RING
    # ======================================================

    def draw_hex_ring(
        self,
        painter,
        center_x,
        center_y,
        radius
    ):
        points = []

        for i in range(6):
            angle = math.radians(
                60 * i - 30
            )

            x = (
                center_x
                + math.cos(angle)
                * radius
            )

            y = (
                center_y
                + math.sin(angle)
                * radius
            )

            points.append(
                (int(x), int(y))
            )

        for i in range(6):
            start = points[i]
            end = points[
                (i + 1) % 6
            ]

            painter.drawLine(
                start[0],
                start[1],
                end[0],
                end[1]
            )
            
    # ======================================================
    # ORB CLICK
    # ======================================================

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

        super().mousePressEvent(event)