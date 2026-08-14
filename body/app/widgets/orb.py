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
    SLEEPING = "sleeping"
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

        self.scale = 1.0

        # ==================================================
        # JARVIS STATE
        # ==================================================

        self.state = OrbState.IDLE

        # ==================================================
        # THEME
        # ==================================================

        self.theme = "dark"

        # ==================================================
        # ANIMATION
        # ==================================================

        self.rotation = 0
        self.pulse = 0

        # ==================================================
        # AUDIO REACTIVITY
        # ==================================================

        self.audio_level = 0.0
        self.target_audio_level = 0.0

        # ==================================================
        # ANIMATION TIMER
        # ==================================================

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    # ======================================================
    # THEME
    # ======================================================

    def set_theme(self, theme):
        """
        Switches the orb between dark and light visual themes.
        """

        theme = str(theme).lower()

        if theme not in (
            "dark",
            "light",
        ):
            theme = "dark"

        self.theme = theme
        self.update()

    # ======================================================
    # THEME COLORS
    # ======================================================

    def get_theme_colors(self):
        """
        Returns the main orb colors for the active theme.
        """

        if self.theme == "light":

            return {
                "glow": QColor(
                    0,
                    145,
                    190,
                    170,
                ),

                "primary": QColor(
                    0,
                    150,
                    190,
                    220,
                ),

                "secondary": QColor(
                    0,
                    105,
                    150,
                    150,
                ),

                "bright": QColor(
                    0,
                    125,
                    165,
                    235,
                ),

                "dark": QColor(
                    4,
                    32,
                    45,
                    255,
                ),

                "housing_mid": QColor(
                    12,
                    58,
                    72,
                    255,
                ),

                "housing_dark": QColor(
                    3,
                    18,
                    27,
                    255,
                ),

                "white": QColor(
                    225,
                    250,
                    255,
                    245,
                ),

                "core": QColor(
                    0,
                    185,
                    220,
                    255,
                ),
            }

        return {
            "glow": QColor(
                0,
                217,
                255,
                255,
            ),

            "primary": QColor(
                0,
                217,
                255,
                210,
            ),

            "secondary": QColor(
                0,
                217,
                255,
                100,
            ),

            "bright": QColor(
                0,
                217,
                255,
                220,
            ),

            "dark": QColor(
                2,
                8,
                14,
                255,
            ),

            "housing_mid": QColor(
                20,
                65,
                80,
                255,
            ),

            "housing_dark": QColor(
                8,
                25,
                35,
                255,
            ),

            "white": QColor(
                235,
                255,
                255,
                255,
            ),

            "core": QColor(
                0,
                230,
                255,
                255,
            ),
        }

    # ======================================================
    # ANIMATION
    # ======================================================

    def animate(self):

        self.rotation = (
            self.rotation + 0.8
        ) % 360

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

        self.audio_level += (
            self.target_audio_level
            - self.audio_level
        ) * 0.18

        self.update()

    # ======================================================
    # STATE
    # ======================================================

    def set_state(self, state):

        self.state = state
        self.update()

    # ======================================================
    # SCALE
    # ======================================================

    def set_scale(self, scale):

        self.scale = max(
            0.80,
            min(
                1.40,
                float(scale),
            ),
        )

        self.update()

    # ======================================================
    # AUDIO LEVEL
    # ======================================================

    def set_audio_level(self, level):

        level = max(
            0.0,
            min(
                1.0,
                float(level),
            ),
        )

        self.target_audio_level = level

    # ======================================================
    # MOUSE CLICK
    # ======================================================

    def mousePressEvent(self, event):

        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):

            self.clicked.emit()

        super().mousePressEvent(event)

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
        # THEME
        # ==================================================

        colors = self.get_theme_colors()

        primary = colors["primary"]
        secondary = colors["secondary"]
        bright = colors["bright"]
        glow_color = colors["glow"]
        dark = colors["dark"]
        housing_mid = colors["housing_mid"]
        housing_dark = colors["housing_dark"]
        white = colors["white"]
        core_color = colors["core"]

        # ==================================================
        # CENTER
        # ==================================================

        center_x = self.width() / 2
        center_y = self.height() / 2

        center = (
            center_x,
            center_y,
        )

        # ==================================================
        # RESPONSIVE SIZE
        # ==================================================

        base_radius = (
            min(
                self.width(),
                self.height(),
            )
            * 0.38
            * self.scale
        )

        breathing = (
            math.sin(self.pulse)
            * 0.025
        )

        if self.state == OrbState.LISTENING:

            breathing = (
                math.sin(self.pulse)
                * 0.015
            )

        voice_reaction = (
            self.audio_level
            * 0.15
        )

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

        glow_strength += int(
            self.audio_level * 80
        )

        glow_strength = min(
            glow_strength,
            255,
        )

        # ==================================================
        # OUTER GLOW
        # ==================================================

        glow_radius = radius * 1.18

        glow = QRadialGradient(
            center_x,
            center_y,
            glow_radius,
        )

        glow.setColorAt(
            0.0,
            QColor(
                glow_color.red(),
                glow_color.green(),
                glow_color.blue(),
                glow_strength,
            ),
        )

        glow.setColorAt(
            0.45,
            QColor(
                glow_color.red(),
                glow_color.green(),
                glow_color.blue(),
                glow_strength // 2,
            ),
        )

        glow.setColorAt(
            1.0,
            QColor(
                glow_color.red(),
                glow_color.green(),
                glow_color.blue(),
                0,
            ),
        )

        painter.setBrush(glow)

        painter.drawEllipse(
            int(
                center_x
                - glow_radius
            ),
            int(
                center_y
                - glow_radius
            ),
            int(
                glow_radius * 2
            ),
            int(
                glow_radius * 2
            ),
        )

        # ==================================================
        # OUTER THIN RINGS
        # ==================================================

        self.draw_circle(
            painter,
            center,
            radius * 0.98,
            primary,
            1,
        )

        self.draw_circle(
            painter,
            center,
            radius * 0.91,
            secondary,
            1,
        )

        self.draw_circle(
            painter,
            center,
            radius * 0.84,
            QColor(
                primary.red(),
                primary.green(),
                primary.blue(),
                75,
            ),
            1,
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
            bright,
        )

        self.draw_arc(
            painter,
            center,
            radius * 0.94,
            self.rotation + 150,
            45,
            2,
            QColor(
                primary.red(),
                primary.green(),
                primary.blue(),
                130,
            ),
        )

        self.draw_arc(
            painter,
            center,
            radius * 0.94,
            self.rotation + 270,
            80,
            2,
            QColor(
                primary.red(),
                primary.green(),
                primary.blue(),
                100,
            ),
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
            QColor(
                primary.red(),
                primary.green(),
                primary.blue(),
                170,
            ),
        )

        self.draw_arc(
            painter,
            center,
            radius * 0.76,
            -self.rotation * 1.4 + 180,
            75,
            2,
            QColor(
                primary.red(),
                primary.green(),
                primary.blue(),
                100,
            ),
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

            dot_alpha = min(
                255,
                150
                + int(
                    self.audio_level
                    * 105
                ),
            )

            painter.setBrush(
                QColor(
                    primary.red(),
                    primary.green(),
                    primary.blue(),
                    dot_alpha,
                )
            )

            painter.drawEllipse(
                int(
                    x
                    - dot_size / 2
                ),
                int(
                    y
                    - dot_size / 2
                ),
                dot_size,
                dot_size,
            )

        # ==================================================
        # SEGMENTED RING
        # ==================================================

        segment_radius = (
            radius * 0.58
        )

        for i in range(24):

            start_angle = (
                i * 15
                + self.rotation * 0.35
            )

            if i % 2 == 0:

                color = QColor(
                    white.red(),
                    white.green(),
                    white.blue(),
                    235,
                )

                width = 5

            else:

                color = QColor(
                    primary.red(),
                    primary.green(),
                    primary.blue(),
                    65,
                )

                width = 3

            self.draw_arc(
                painter,
                center,
                segment_radius,
                start_angle,
                9,
                width,
                color,
            )

        # ==================================================
        # INNER RINGS
        # ==================================================

        self.draw_circle(
            painter,
            center,
            radius * 0.49,
            QColor(
                primary.red(),
                primary.green(),
                primary.blue(),
                140,
            ),
            2,
        )

        self.draw_circle(
            painter,
            center,
            radius * 0.42,
            QColor(
                primary.red(),
                primary.green(),
                primary.blue(),
                80,
            ),
            1,
        )

        # ==================================================
        # ARC REACTOR CORE
        # ==================================================

        core_radius = radius * 0.31

        # ==================================================
        # CORE GLOW
        # ==================================================

        core_glow = QRadialGradient(
            center_x,
            center_y,
            core_radius * 1.65,
        )

        core_glow.setColorAt(
            0.0,
            QColor(
                255,
                255,
                255,
                240,
            ),
        )

        core_glow.setColorAt(
            0.18,
            QColor(
                120,
                245,
                255,
                230,
            ),
        )

        core_glow.setColorAt(
            0.45,
            QColor(
                core_color.red(),
                core_color.green(),
                core_color.blue(),
                150,
            ),
        )

        core_glow.setColorAt(
            0.75,
            QColor(
                0,
                120,
                180,
                55,
            ),
        )

        core_glow.setColorAt(
            1.0,
            QColor(
                core_color.red(),
                core_color.green(),
                core_color.blue(),
                0,
            ),
        )

        painter.setBrush(
            core_glow
        )

        painter.drawEllipse(
            int(
                center_x
                - core_radius * 1.65
            ),
            int(
                center_y
                - core_radius * 1.65
            ),
            int(
                core_radius * 3.3
            ),
            int(
                core_radius * 3.3
            ),
        )

        # ==================================================
        # DARK REACTOR HOUSING
        # ==================================================

        housing_radius = (
            core_radius * 0.98
        )

        housing = QRadialGradient(
            center_x,
            center_y,
            housing_radius,
        )

        housing.setColorAt(
            0.0,
            housing_mid,
        )

        housing.setColorAt(
            0.55,
            housing_dark,
        )

        housing.setColorAt(
            1.0,
            dark,
        )

        painter.setBrush(
            housing
        )

        painter.setPen(
            QPen(
                primary,
                2,
            )
        )

        painter.drawEllipse(
            int(
                center_x
                - housing_radius
            ),
            int(
                center_y
                - housing_radius
            ),
            int(
                housing_radius * 2
            ),
            int(
                housing_radius * 2
            ),
        )

        # ==================================================
        # ARC REACTOR OUTER RING
        # ==================================================

        self.draw_circle(
            painter,
            center,
            core_radius * 0.86,
            white,
            3,
        )

        self.draw_circle(
            painter,
            center,
            core_radius * 0.72,
            QColor(
                primary.red(),
                primary.green(),
                primary.blue(),
                180,
            ),
            2,
        )

        # ==================================================
        # REACTOR SEGMENTS
        # ==================================================

        reactor_radius = (
            core_radius * 0.78
        )

        for i in range(12):

            start_angle = (
                self.rotation * 0.35
                + i * 30
            )

            if i % 2 == 0:

                color = QColor(
                    white.red(),
                    white.green(),
                    white.blue(),
                    235,
                )

                width = 5

            else:

                color = QColor(
                    primary.red(),
                    primary.green(),
                    primary.blue(),
                    120,
                )

                width = 3

            self.draw_arc(
                painter,
                center,
                reactor_radius,
                start_angle,
                17,
                width,
                color,
            )

        # ==================================================
        # ARC REACTOR THREE-SPOKE STRUCTURE
        # ==================================================

        spoke_radius = (
            core_radius * 0.62
        )

        painter.setBrush(
            Qt.BrushStyle.NoBrush
        )

        painter.setPen(
            QPen(
                white,
                4,
            )
        )

        for i in range(3):

            angle = math.radians(
                self.rotation * 0.15
                + i * 120
            )

            inner_x = (
                center_x
                + math.cos(angle)
                * core_radius
                * 0.18
            )

            inner_y = (
                center_y
                + math.sin(angle)
                * core_radius
                * 0.18
            )

            outer_x = (
                center_x
                + math.cos(angle)
                * spoke_radius
            )

            outer_y = (
                center_y
                + math.sin(angle)
                * spoke_radius
            )

            painter.drawLine(
                int(inner_x),
                int(inner_y),
                int(outer_x),
                int(outer_y),
            )

        # ==================================================
        # INNER REACTOR RING
        # ==================================================

        inner_radius = (
            core_radius * 0.46
        )

        self.draw_circle(
            painter,
            center,
            inner_radius,
            white,
            3,
        )

        # ==================================================
        # REACTOR CORE GLOW
        # ==================================================

        reactor_core = QRadialGradient(
            center_x,
            center_y,
            inner_radius,
        )

        reactor_core.setColorAt(
            0.0,
            QColor(
                255,
                255,
                255,
                255,
            ),
        )

        reactor_core.setColorAt(
            0.20,
            QColor(
                180,
                250,
                255,
                255,
            ),
        )

        reactor_core.setColorAt(
            0.55,
            core_color,
        )

        reactor_core.setColorAt(
            1.0,
            QColor(
                0,
                80,
                130,
                255,
            ),
        )

        painter.setBrush(
            reactor_core
        )

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.drawEllipse(
            int(
                center_x
                - inner_radius
            ),
            int(
                center_y
                - inner_radius
            ),
            int(
                inner_radius * 2
            ),
            int(
                inner_radius * 2
            ),
        )

        # ==================================================
        # CENTRAL ARC REACTOR
        # ==================================================

        central_radius = (
            core_radius * 0.23
        )

        central_glow = QRadialGradient(
            center_x,
            center_y,
            central_radius * 2,
        )

        central_glow.setColorAt(
            0.0,
            QColor(
                255,
                255,
                255,
                255,
            ),
        )

        central_glow.setColorAt(
            0.30,
            QColor(
                0,
                245,
                255,
                255,
            ),
        )

        central_glow.setColorAt(
            0.65,
            QColor(
                0,
                180,
                230,
                150,
            ),
        )

        central_glow.setColorAt(
            1.0,
            QColor(
                0,
                217,
                255,
                0,
            ),
        )

        painter.setBrush(
            central_glow
        )

        painter.drawEllipse(
            int(
                center_x
                - central_radius * 2
            ),
            int(
                center_y
                - central_radius * 2
            ),
            int(
                central_radius * 4
            ),
            int(
                central_radius * 4
            ),
        )

        # ==================================================
        # CENTRAL LIGHT
        # ==================================================

        painter.setBrush(
            QColor(
                235,
                255,
                255,
                255,
            )
        )

        painter.drawEllipse(
            int(
                center_x
                - central_radius * 0.32
            ),
            int(
                center_y
                - central_radius * 0.32
            ),
            int(
                central_radius * 0.64
            ),
            int(
                central_radius * 0.64
            ),
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
        width,
    ):

        center_x, center_y = center

        painter.setBrush(
            Qt.BrushStyle.NoBrush
        )

        painter.setPen(
            QPen(
                color,
                width,
            )
        )

        painter.drawEllipse(
            int(
                center_x - radius
            ),
            int(
                center_y - radius
            ),
            int(
                radius * 2
            ),
            int(
                radius * 2
            ),
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
        color,
    ):

        center_x, center_y = center

        painter.setBrush(
            Qt.BrushStyle.NoBrush
        )

        painter.setPen(
            QPen(
                color,
                width,
            )
        )

        painter.drawArc(
            int(
                center_x - radius
            ),
            int(
                center_y - radius
            ),
            int(
                radius * 2
            ),
            int(
                radius * 2
            ),
            int(
                -start_angle * 16
            ),
            int(
                -span_angle * 16
            ),
        )

    # ======================================================
    # DRAW HEXAGON RING
    # ======================================================

    def draw_hex_ring(
        self,
        painter,
        center_x,
        center_y,
        radius,
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
                (
                    int(x),
                    int(y),
                )
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
                end[1],
            )