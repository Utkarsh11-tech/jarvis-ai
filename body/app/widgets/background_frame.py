from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QPainter,
    QPen,
    QColor,
    QRadialGradient,
    QLinearGradient,
)
from PySide6.QtWidgets import QWidget


# ============================================================
# BACKGROUND
# ============================================================


class BackgroundFrame(QWidget):

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

    # ========================================================
    # THEME
    # ========================================================

    def set_theme(
        self,
        theme,
    ):

        self.theme = theme.lower()

        self.update()

    # ========================================================
    # PAINT
    # ========================================================

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

        center_x = width // 2
        center_y = int(
            height * 0.35
        )

        # ========================================================
        # COLORS
        # ========================================================

        if self.theme == "light":

            base_top = QColor(
                235,
                249,
                253,
            )

            base_middle = QColor(
                222,
                244,
                249,
            )

            base_bottom = QColor(
                207,
                236,
                244,
            )

            glow_primary = QColor(
                0,
                150,
                190,
                35,
            )

            glow_secondary = QColor(
                0,
                110,
                160,
                20,
            )

            line_color = QColor(
                0,
                120,
                160,
                45,
            )

            ring_color = QColor(
                0,
                120,
                160,
                30,
            )

            horizontal_color = QColor(
                0,
                150,
                190,
                25,
            )

            tick_color = QColor(
                0,
                120,
                160,
                45,
            )

            dot_color = QColor(
                0,
                130,
                175,
                75,
            )

            top_color = QColor(
                0,
                120,
                160,
                50,
            )

        else:

            base_top = QColor(
                1,
                5,
                10,
            )

            base_middle = QColor(
                2,
                9,
                17,
            )

            base_bottom = QColor(
                0,
                4,
                9,
            )

            glow_primary = QColor(
                0,
                90,
                140,
                32,
            )

            glow_secondary = QColor(
                0,
                55,
                100,
                20,
            )

            line_color = QColor(
                0,
                110,
                170,
                30,
            )

            ring_color = QColor(
                0,
                120,
                180,
                15,
            )

            horizontal_color = QColor(
                0,
                160,
                220,
                18,
            )

            tick_color = QColor(
                0,
                160,
                220,
                35,
            )

            dot_color = QColor(
                0,
                180,
                240,
                65,
            )

            top_color = QColor(
                0,
                150,
                210,
                40,
            )

        # ========================================================
        # BASE GRADIENT
        # ========================================================

        base_gradient = QLinearGradient(
            0,
            0,
            0,
            height,
        )

        base_gradient.setColorAt(
            0.0,
            base_top,
        )

        base_gradient.setColorAt(
            0.5,
            base_middle,
        )

        base_gradient.setColorAt(
            1.0,
            base_bottom,
        )

        painter.fillRect(
            self.rect(),
            base_gradient,
        )

        # ========================================================
        # CENTRAL GLOW
        # ========================================================

        glow = QRadialGradient(
            center_x,
            center_y,
            min(
                width,
                height,
            ) * 0.48,
        )

        glow.setColorAt(
            0.0,
            glow_primary,
        )

        glow.setColorAt(
            0.30,
            glow_secondary,
        )

        glow.setColorAt(
            0.65,
            QColor(
                0,
                25,
                55,
                8,
            ),
        )

        glow.setColorAt(
            1.0,
            QColor(
                0,
                0,
                0,
                0,
            ),
        )

        painter.fillRect(
            self.rect(),
            glow,
        )

        # ========================================================
        # HORIZONTAL GLOW
        # ========================================================

        horizontal_glow = QLinearGradient(
            0,
            center_y,
            width,
            center_y,
        )

        horizontal_glow.setColorAt(
            0.0,
            QColor(
                0,
                0,
                0,
                0,
            ),
        )

        horizontal_glow.setColorAt(
            0.35,
            horizontal_color,
        )

        horizontal_glow.setColorAt(
            0.5,
            horizontal_color,
        )

        horizontal_glow.setColorAt(
            0.65,
            horizontal_color,
        )

        horizontal_glow.setColorAt(
            1.0,
            QColor(
                0,
                0,
                0,
                0,
            ),
        )

        painter.fillRect(
            0,
            center_y - 1,
            width,
            2,
            horizontal_glow,
        )

        # ========================================================
        # CIRCUIT LINES
        # ========================================================

        painter.setPen(
            QPen(
                line_color,
                1,
            )
        )

        left_x = 55

        # LEFT

        painter.drawLine(
            left_x,
            155,
            left_x + 150,
            155,
        )

        painter.drawLine(
            left_x + 150,
            155,
            left_x + 185,
            190,
        )

        painter.drawLine(
            left_x + 185,
            190,
            left_x + 260,
            190,
        )

        painter.drawLine(
            left_x,
            205,
            left_x + 105,
            205,
        )

        painter.drawLine(
            left_x + 105,
            205,
            left_x + 130,
            230,
        )

        painter.drawLine(
            left_x + 130,
            230,
            left_x + 220,
            230,
        )

        # RIGHT

        right_x = width - 55

        painter.drawLine(
            right_x - 150,
            155,
            right_x,
            155,
        )

        painter.drawLine(
            right_x - 185,
            190,
            right_x - 150,
            155,
        )

        painter.drawLine(
            right_x - 260,
            190,
            right_x - 185,
            190,
        )

        painter.drawLine(
            right_x - 105,
            205,
            right_x,
            205,
        )

        painter.drawLine(
            right_x - 130,
            230,
            right_x - 105,
            205,
        )

        painter.drawLine(
            right_x - 220,
            230,
            right_x - 130,
            230,
        )

        # ========================================================
        # SIDE TECHNICAL LINES
        # ========================================================

        for y in range(
            270,
            height - 110,
            55,
        ):

            painter.drawLine(
                55,
                y,
                130,
                y,
            )

            painter.drawLine(
                130,
                y,
                155,
                y + 18,
            )

            painter.drawLine(
                155,
                y + 18,
                220,
                y + 18,
            )

            painter.drawLine(
                width - 55,
                y,
                width - 130,
                y,
            )

            painter.drawLine(
                width - 130,
                y,
                width - 155,
                y + 18,
            )

            painter.drawLine(
                width - 155,
                y + 18,
                width - 220,
                y + 18,
            )

        # ========================================================
        # DATA TICKS
        # ========================================================

        painter.setPen(
            QPen(
                tick_color,
                1,
            )
        )

        for y in range(
            160,
            height - 130,
            16,
        ):

            painter.drawLine(
                80,
                y,
                95,
                y,
            )

            painter.drawLine(
                width - 95,
                y,
                width - 80,
                y,
            )

        # ========================================================
        # DOTS
        # ========================================================

        painter.setPen(
            QPen(
                dot_color,
                2,
            )
        )

        dots = [
            (55, 155),
            (55, 205),
            (130, 230),
            (width - 55, 155),
            (width - 55, 205),
            (width - 130, 230),
        ]

        for x, y in dots:

            painter.drawPoint(
                x,
                y,
            )

        # ========================================================
        # HUD RINGS
        # ========================================================

        painter.setPen(
            QPen(
                ring_color,
                1,
            )
        )

        ring_center_y = int(
            height * 0.36
        )

        for radius in (
            260,
            310,
            365,
        ):

            painter.drawEllipse(
                center_x - radius,
                ring_center_y - radius,
                radius * 2,
                radius * 2,
            )

        # ========================================================
        # TOP DATA LINES
        # ========================================================

        painter.setPen(
            QPen(
                top_color,
                1,
            )
        )

        painter.drawLine(
            55,
            78,
            300,
            78,
        )

        painter.drawLine(
            700,
            78,
            width - 55,
            78,
        )

        painter.drawLine(
            55,
            92,
            210,
            92,
        )

        painter.drawLine(
            width - 210,
            92,
            width - 55,
            92,
        )

        # ========================================================
        # BOTTOM DATA LINES
        # ========================================================

        painter.drawLine(
            55,
            height - 50,
            300,
            height - 50,
        )

        painter.drawLine(
            700,
            height - 50,
            width - 55,
            height - 50,
        )

        painter.drawLine(
            55,
            height - 36,
            210,
            height - 36,
        )

        painter.drawLine(
            width - 210,
            height - 36,
            width - 55,
            height - 36,
        )
