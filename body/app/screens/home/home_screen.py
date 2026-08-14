from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QPainter,
    QPen,
    QColor,
    QRadialGradient,
    QLinearGradient,
    QIcon,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QSystemTrayIcon,
    QMenu,
    QStackedWidget,
    QToolButton,
)

from body.app.widgets.overlay import JarvisOverlay
from body.app.widgets.orb import OrbWidget, OrbState
from body.app.widgets.microphone import Microphone
from body.app.widgets.conversation import ConversationWidget
from body.app.widgets.chat_input import ChatInput
from body.app.widgets.chrome_profile_selector import (
    ChromeProfileSelector,
)

from body.app.settings_manager import SettingsManager
from body.app.screens.settings.settings_screen import (
    SettingsScreen,
)

from bridge.bridge import JarvisBridge


# ==================================================
# BACKGROUND
# ==================================================


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

    # ==================================================
    # SET THEME
    # ==================================================

    def set_theme(
        self,
        theme,
    ):

        self.theme = theme.lower()

        self.update()

    # ==================================================
    # PAINT
    # ==================================================

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

        # ==========================================
        # THEME COLORS
        # ==========================================

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

        # ==========================================
        # BASE BACKGROUND
        # ==========================================

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

        # ==========================================
        # CENTRAL GLOW
        # ==========================================

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

        # ==========================================
        # HORIZONTAL CENTER GLOW
        # ==========================================

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

        # ==========================================
        # CIRCUIT LINES
        # ==========================================

        painter.setPen(
            QPen(
                line_color,
                1,
            )
        )

        # ==========================================
        # LEFT CIRCUIT
        # ==========================================

        left_x = 55

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

        # ==========================================
        # RIGHT CIRCUIT
        # ==========================================

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

        # ==========================================
        # SIDE TECHNICAL LINES
        # ==========================================

        painter.setPen(
            QPen(
                line_color,
                1,
            )
        )

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

        for y in range(
            270,
            height - 110,
            55,
        ):

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

        # ==========================================
        # DATA TICKS
        # ==========================================

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

        # ==========================================
        # TECHNICAL DOTS
        # ==========================================

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

        # ==========================================
        # HUD RINGS
        # ==========================================

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

        # ==========================================
        # TOP DATA LINES
        # ==========================================

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

        # ==========================================
        # BOTTOM DATA LINES
        # ==========================================

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


# ==================================================
# HUD FRAME
# ==================================================


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

    # ==================================================
    # SET THEME
    # ==================================================

    def set_theme(
        self,
        theme,
    ):

        self.theme = theme.lower()

        self.update()

    # ==================================================
    # PAINT
    # ==================================================

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

        # ==========================================
        # FRAME
        # ==========================================

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

        # ==========================================
        # SIDE MARKERS
        # ==========================================

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

        # ==========================================
        # HUD TICKS
        # ==========================================

        tick_color = (
            marker_color
        )

        painter.setPen(
            QPen(
                tick_color,
                1,
            )
        )

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


# ==================================================
# MAIN WINDOW
# ==================================================


class MainWindow(QMainWindow):

    def __init__(
        self,
        bridge,
    ):
        super().__init__()

        # ==========================================
        # TRAY
        # ==========================================

        self.tray_icon = None
        self.tray_menu = None
        self._exiting = False

        # ==========================================
        # SETTINGS
        # ==========================================

        self.settings_manager = (
            SettingsManager()
        )

        # ==========================================
        # UI SCALE
        # ==========================================

        self.ui_scale = 1.0

        # ==========================================
        # WINDOW
        # ==========================================

        self.setWindowTitle(
            "J.A.R.V.I.S"
        )

        self.resize(
            1000,
            650,
        )

        # ==========================================
        # CENTRAL WIDGET
        # ==========================================

        self.central_widget = QWidget()

        self.setCentralWidget(
            self.central_widget
        )

        # ==========================================
        # PAGE STACK
        # ==========================================

        self.page_stack = QStackedWidget(
            self.central_widget
        )

        self.page_stack.setGeometry(
            self.central_widget.rect()
        )

        # ==========================================
        # HOME PAGE
        # ==========================================

        self.home_page = QWidget()

        self.page_stack.addWidget(
            self.home_page
        )

        # ==========================================
        # BACKGROUND
        # ==========================================

        self.background = BackgroundFrame(
            self.central_widget
        )

        self.background.setGeometry(
            self.central_widget.rect()
        )

        self.background.lower()

        # ==========================================
        # MAIN LAYOUT
        # ==========================================

        self.main_layout = QVBoxLayout(
            self.home_page
        )

        self.main_layout.setContentsMargins(
            38,
            28,
            38,
            24,
        )

        self.main_layout.setSpacing(
            10
        )

        # ==========================================
        # HEADER
        # ==========================================

        self.header_row = QHBoxLayout()

        self.header_row.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        # ==========================================
        # SETTINGS BUTTON
        # ==========================================

        self.settings_button = QToolButton()

        self.settings_button.setText(
            "⚙"
        )

        self.settings_button.setToolTip(
            "Settings"
        )

        self.settings_button.setFixedSize(
            42,
            42,
        )

        self.settings_button.setStyleSheet(
            """
            QToolButton {
                background: transparent;
                color: #5C91B5;
                border: 1px solid transparent;
                border-radius: 7px;
                font-size: 22px;
            }

            QToolButton:hover {
                background: rgba(0, 150, 210, 25);
                color: #00D9FF;
                border: 1px solid rgba(0, 217, 255, 80);
            }

            QToolButton:pressed {
                background: rgba(0, 150, 210, 45);
                color: #DDEFFF;
            }
            """
        )

        self.settings_button.clicked.connect(
            self.show_settings_page
        )

        self.header_row.addWidget(
            self.settings_button,
            0,
            Qt.AlignmentFlag.AlignLeft,
        )

        # ==========================================
        # HEADER
        # ==========================================

        self.header = QLabel(
            "J.A.R.V.I.S"
        )

        self.header.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.header.setStyleSheet(
            """
            QLabel {
                background: transparent;
                color: #DDEFFF;
                font-family: "Orbitron", "Eurostile", "Arial";
                font-size: 27px;
                font-weight: 700;
                letter-spacing: 8px;
            }
            """
        )

        self.header_row.addWidget(
            self.header,
            1,
        )

        self.header_row.addSpacing(
            42
        )

        self.main_layout.addLayout(
            self.header_row,
            1,
        )

        # ==========================================
        # HUD FRAME
        # ==========================================

        self.hud_frame = HUDFrame(
            self.central_widget
        )

        self.hud_frame.setGeometry(
            self.central_widget.rect()
        )

        self.hud_frame.raise_()

        # ==========================================
        # ORB
        # ==========================================

        self.orb = OrbWidget()

        # ==========================================
        # MICROPHONE
        # ==========================================

        self.microphone = Microphone()

        # ==========================================
        # BRIDGE
        # ==========================================

        self.bridge = bridge

        self.bridge.state_changed.connect(
            self.handle_state_change
        )

        self.bridge.response_received.connect(
            self.handle_jarvis_response
        )

        self.bridge.profile_selection_requested.connect(
            self.handle_profile_selection
        )

        # ==========================================
        # OVERLAY
        # ==========================================

        self.overlay = JarvisOverlay()

        self.bridge.wake_detected.connect(
            self.show_wake_overlay
        )

        # ==========================================
        # MICROPHONE → ORB
        # ==========================================

        self.microphone.level_changed.connect(
            self.orb.set_audio_level
        )

        # ==========================================
        # MICROPHONE → OVERLAY
        # ==========================================

        self.microphone.level_changed.connect(
            self.overlay.set_audio_level
        )

        # ==========================================
        # ORB CLICK
        # ==========================================

        self.orb.clicked.connect(
            self.toggle_listening
        )

        self.orb.set_state(
            OrbState.IDLE
        )

        # ==========================================
        # STATUS
        # ==========================================

        self.status = QLabel(
            "STATUS  :  WAITING FOR COMMAND"
        )

        self.status.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.status.setStyleSheet(
            """
            QLabel {
                background: transparent;
                color: #5C91B5;
                font-family: "Orbitron", "Eurostile", "Arial";
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 2px;
            }
            """
        )

        # ==========================================
        # CHAT
        # ==========================================

        self.chat = ConversationWidget()

        # ==========================================
        # CHAT INPUT
        # ==========================================

        self.chat_input = ChatInput()

        self.chat_input.message_sent.connect(
            self.handle_text_message
        )

        # ==========================================
        # FOOTER
        # ==========================================

        self.footer = QLabel(
            "J.A.R.V.I.S  •  SYSTEM ONLINE"
        )

        self.footer.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.footer.setStyleSheet(
            """
            QLabel {
                background: transparent;
                color: #34546B;
                font-family: "Orbitron", "Eurostile", "Arial";
                font-size: 10px;
                font-weight: 600;
                letter-spacing: 3px;
            }
            """
        )

        # ==========================================
        # ADD HOME WIDGETS
        # ==========================================

        self.main_layout.addWidget(
            self.orb,
            6,
        )

        self.main_layout.addWidget(
            self.status,
            1,
        )

        self.main_layout.addWidget(
            self.chat,
            2,
        )

        self.main_layout.addWidget(
            self.chat_input,
        )

        self.main_layout.addWidget(
            self.footer,
            1,
        )

        # ==========================================
        # PROFILE SELECTOR
        # ==========================================

        self.profile_selector = None

        # ==========================================
        # SETTINGS SCREEN
        # ==========================================

        self.settings_screen = SettingsScreen(
            self.settings_manager,
            self,
        )

        self.page_stack.addWidget(
            self.settings_screen
        )

        self.settings_screen.back_requested.connect(
            self.show_home_page
        )

        self.settings_screen.theme_changed.connect(
            self.apply_theme
        )

        # ==========================================
        # SYSTEM TRAY
        # ==========================================

        self.setup_system_tray()

        # ==========================================
        # APPLY SAVED THEME
        # ==========================================

        self.apply_theme(
            self.settings_manager.theme
        )

        # ==========================================
        # INITIAL UI SCALE
        # ==========================================

        self.update_ui_scale()

    # ==================================================
    # SYSTEM TRAY
    # ==================================================

    def setup_system_tray(
        self,
    ):

        if not QSystemTrayIcon.isSystemTrayAvailable():

            return

        pixmap = QPixmap(
            64,
            64,
        )

        pixmap.fill(
            Qt.GlobalColor.transparent
        )

        painter = QPainter(
            pixmap
        )

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        painter.setPen(
            QPen(
                QColor(
                    0,
                    217,
                    255,
                    190,
                ),
                3,
            )
        )

        painter.setBrush(
            QColor(
                2,
                15,
                25,
            )
        )

        painter.drawEllipse(
            8,
            8,
            48,
            48,
        )

        painter.setPen(
            QPen(
                QColor(
                    0,
                    217,
                    255,
                    220,
                ),
                2,
            )
        )

        painter.setBrush(
            QColor(
                0,
                120,
                180,
            )
        )

        painter.drawEllipse(
            18,
            18,
            28,
            28,
        )

        painter.end()

        self.tray_icon = QSystemTrayIcon(
            QIcon(pixmap),
            self,
        )

        self.tray_icon.setToolTip(
            "J.A.R.V.I.S"
        )

        self.tray_menu = QMenu()

        open_action = self.tray_menu.addAction(
            "Open J.A.R.V.I.S"
        )

        open_action.triggered.connect(
            self.restore_from_tray
        )

        listen_action = self.tray_menu.addAction(
            "Start Listening"
        )

        listen_action.triggered.connect(
            self.start_listening_from_tray
        )

        self.tray_menu.addSeparator()

        exit_action = self.tray_menu.addAction(
            "Exit J.A.R.V.I.S"
        )

        exit_action.triggered.connect(
            self.exit_from_tray
        )

        self.tray_icon.setContextMenu(
            self.tray_menu
        )

        self.tray_icon.activated.connect(
            self.handle_tray_activation
        )

        self.tray_icon.show()

    # ==================================================
    # RESTORE
    # ==================================================

    def restore_from_tray(
        self,
    ):

        self.show()
        self.showNormal()
        self.raise_()
        self.activateWindow()

    # ==================================================
    # START LISTENING FROM TRAY
    # ==================================================

    def start_listening_from_tray(
        self,
    ):

        self.restore_from_tray()

        if self.orb.state in (
            OrbState.IDLE,
            OrbState.SLEEPING,
        ):

            self.toggle_listening()

    # ==================================================
    # TRAY ACTIVATION
    # ==================================================

    def handle_tray_activation(
        self,
        reason,
    ):

        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):

            self.restore_from_tray()

    # ==================================================
    # CLOSE
    # ==================================================

    def closeEvent(
        self,
        event,
    ):

        if self._exiting:

            event.accept()

            return

        if self.tray_icon is not None:

            self.hide()

            self.tray_icon.showMessage(
                "J.A.R.V.I.S",
                "JARVIS is still running in the system tray.",
                QSystemTrayIcon.MessageIcon.Information,
                2000,
            )

            event.ignore()

        else:

            event.accept()

    # ==================================================
    # EXIT
    # ==================================================

    def exit_from_tray(
        self,
    ):

        self._exiting = True

        if self.tray_icon is not None:

            self.tray_icon.hide()

        QApplication.quit()

    # ==================================================
    # PAGE NAVIGATION
    # ==================================================

    def show_home_page(
        self,
    ):

        self.page_stack.setCurrentWidget(
            self.home_page
        )

    def show_settings_page(
        self,
    ):

        self.page_stack.setCurrentWidget(
            self.settings_screen
        )

    # ==================================================
    # THEME
    # ==================================================

    def apply_theme(
        self,
        theme,
    ):

        theme = theme.lower()

        if hasattr(self, "orb"):
            self.orb.set_theme(theme)

        if hasattr(self, "chat"):
            self.chat.apply_theme(theme)

        if hasattr(self, "chat_input"):
            self.chat_input.apply_theme(theme)

        # ==========================================
        # BACKGROUND
        # ==========================================

        if hasattr(
            self,
            "background",
        ):

            self.background.set_theme(
                theme
            )

        # ==========================================
        # HUD
        # ==========================================

        if hasattr(
            self,
            "hud_frame",
        ):

            self.hud_frame.set_theme(
                theme
            )

        # ==========================================
        # SETTINGS
        # ==========================================

        if hasattr(
            self,
            "settings_screen",
        ):

            self.settings_screen.apply_theme(
                theme
            )

        # ==========================================
        # MAIN UI
        # ==========================================

        if theme == "light":

            self.setStyleSheet(
                """
                QMainWindow {
                    background-color: #E8F7FB;
                }

                QWidget {
                    background: transparent;
                    color: #06202D;
                }

                QLabel {
                    background: transparent;
                    color: #06202D;
                }
                """
            )

            self.header.setStyleSheet(
                """
                QLabel {
                    background: transparent;
                    color: #08202C;
                    font-family: "Orbitron", "Eurostile", "Arial";
                    font-size: 27px;
                    font-weight: 700;
                    letter-spacing: 8px;
                }
                """
            )

            self.status.setStyleSheet(
                """
                QLabel {
                    background: transparent;
                    color: #26728A;
                    font-family: "Orbitron", "Eurostile", "Arial";
                    font-size: 11px;
                    font-weight: 600;
                    letter-spacing: 2px;
                }
                """
            )

            self.footer.setStyleSheet(
                """
                QLabel {
                    background: transparent;
                    color: #47849A;
                    font-family: "Orbitron", "Eurostile", "Arial";
                    font-size: 10px;
                    font-weight: 600;
                    letter-spacing: 3px;
                }
                """
            )

        else:

            self.setStyleSheet(
                """
                QMainWindow {
                    background-color: #01050A;
                }

                QWidget {
                    background: transparent;
                    color: #DDEFFF;
                }

                QLabel {
                    background: transparent;
                    color: #DDEFFF;
                }
                """
            )

            self.header.setStyleSheet(
                """
                QLabel {
                    background: transparent;
                    color: #DDEFFF;
                    font-family: "Orbitron", "Eurostile", "Arial";
                    font-size: 27px;
                    font-weight: 700;
                    letter-spacing: 8px;
                }
                """
            )

            self.status.setStyleSheet(
                """
                QLabel {
                    background: transparent;
                    color: #5C91B5;
                    font-family: "Orbitron", "Eurostile", "Arial";
                    font-size: 11px;
                    font-weight: 600;
                    letter-spacing: 2px;
                }
                """
            )

            self.footer.setStyleSheet(
                """
                QLabel {
                    background: transparent;
                    color: #34546B;
                    font-family: "Orbitron", "Eurostile", "Arial";
                    font-size: 10px;
                    font-weight: 600;
                    letter-spacing: 3px;
                }
                """
            )

        self.update_ui_scale()

    # ==================================================
    # RESPONSIVE UI SCALE
    # ==================================================

    def update_ui_scale(
        self,
    ):

        width = self.width()
        height = self.height()

        scale_x = width / 1000.0
        scale_y = height / 650.0

        scale = min(
            scale_x,
            scale_y,
        )

        scale = max(
            0.80,
            min(
                scale,
                1.80,
            ),
        )

        self.ui_scale = scale

        # ==========================================
        # HEADER
        # ==========================================

        header_size = max(
            18,
            int(
                27 * scale
            ),
        )

        header_letter_spacing = max(
            2,
            int(
                8 * scale
            ),
        )

        header_color = (
            "#08202C"
            if self.settings_manager.theme.lower()
            == "light"
            else "#DDEFFF"
        )

        self.header.setStyleSheet(
            f"""
            QLabel {{
                background: transparent;
                color: {header_color};
                font-family: "Orbitron", "Eurostile", "Arial";
                font-size: {header_size}px;
                font-weight: 700;
                letter-spacing: {header_letter_spacing}px;
            }}
            """
        )

        # ==========================================
        # SETTINGS BUTTON
        # ==========================================

        button_size = max(
            32,
            int(
                42 * scale
            ),
        )

        self.settings_button.setFixedSize(
            button_size,
            button_size,
        )

        settings_font_size = max(
            16,
            int(
                22 * scale
            ),
        )

        self.settings_button.setStyleSheet(
            f"""
            QToolButton {{
                background: transparent;
                color: #5C91B5;
                border: 1px solid transparent;
                border-radius: {max(5, int(7 * scale))}px;
                font-size: {settings_font_size}px;
            }}

            QToolButton:hover {{
                background: rgba(0, 150, 210, 25);
                color: #00D9FF;
                border: 1px solid rgba(0, 217, 255, 80);
            }}

            QToolButton:pressed {{
                background: rgba(0, 150, 210, 45);
                color: #DDEFFF;
            }}
            """
        )

        # ==========================================
        # STATUS
        # ==========================================

        status_size = max(
            9,
            int(
                11 * scale
            ),
        )

        status_spacing = max(
            1,
            int(
                2 * scale
            ),
        )

        status_color = (
            "#26728A"
            if self.settings_manager.theme.lower()
            == "light"
            else "#5C91B5"
        )

        self.status.setStyleSheet(
            f"""
            QLabel {{
                background: transparent;
                color: {status_color};
                font-family: "Orbitron", "Eurostile", "Arial";
                font-size: {status_size}px;
                font-weight: 600;
                letter-spacing: {status_spacing}px;
            }}
            """
        )

        # ==========================================
        # FOOTER
        # ==========================================

        footer_size = max(
            8,
            int(
                10 * scale
            ),
        )

        footer_spacing = max(
            1,
            int(
                3 * scale
            ),
        )

        footer_color = (
            "#47849A"
            if self.settings_manager.theme.lower()
            == "light"
            else "#34546B"
        )

        self.footer.setStyleSheet(
            f"""
            QLabel {{
                background: transparent;
                color: {footer_color};
                font-family: "Orbitron", "Eurostile", "Arial";
                font-size: {footer_size}px;
                font-weight: 600;
                letter-spacing: {footer_spacing}px;
            }}
            """
        )

        # ==========================================
        # LAYOUT
        # ==========================================

        self.main_layout.setContentsMargins(
            max(
                24,
                int(
                    38 * scale
                ),
            ),
            max(
                18,
                int(
                    28 * scale
                ),
            ),
            max(
                24,
                int(
                    38 * scale
                ),
            ),
            max(
                18,
                int(
                    24 * scale
                ),
            ),
        )

        self.main_layout.setSpacing(
            max(
                6,
                int(
                    10 * scale
                ),
            )
        )

        self.header_row.setSpacing(
            max(
                4,
                int(
                    8 * scale
                ),
            )
        )

    # ==================================================
    # RESIZE
    # ==================================================

    def resizeEvent(
        self,
        event,
    ):

        super().resizeEvent(
            event
        )

        if hasattr(
            self,
            "background",
        ):

            self.background.setGeometry(
                self.central_widget.rect()
            )

        if hasattr(
            self,
            "hud_frame",
        ):

            self.hud_frame.setGeometry(
                self.central_widget.rect()
            )

        if hasattr(
            self,
            "page_stack",
        ):

            self.page_stack.setGeometry(
                self.central_widget.rect()
            )

        if hasattr(
            self,
            "main_layout",
        ):

            self.update_ui_scale()

    # ==================================================
    # TEXT MESSAGE
    # ==================================================

    def handle_text_message(
        self,
        message,
    ):

        self.chat.add_user_message(
            message
        )

        self.bridge.send_command(
            message
        )

    # ==================================================
    # PROFILE SELECTION
    # ==================================================

    def handle_profile_selection(
        self,
        profiles,
    ):

        self.profile_selector = (
            ChromeProfileSelector(
                profiles,
                self,
            )
        )

        self.profile_selector.profile_selected.connect(
            self.handle_profile_selected
        )

        self.profile_selector.exec()

    # ==================================================
    # PROFILE SELECTED
    # ==================================================

    def handle_profile_selected(
        self,
        profile_directory,
    ):

        self.bridge.send_profile_selection(
            profile_directory
        )

    # ==================================================
    # WAKE OVERLAY
    # ==================================================

    def show_wake_overlay(
        self,
    ):

        active_window = (
            QApplication.activeWindow()
        )

        if (
            active_window is self
            or (
                active_window is not None
                and self.isAncestorOf(
                    active_window
                )
            )
        ):

            self.overlay.hide_overlay()

            return

        self.overlay.show_overlay()

    # ==================================================
    # TOGGLE LISTENING
    # ==================================================

    def toggle_listening(
        self,
    ):

        if self.orb.state in (
            OrbState.IDLE,
            OrbState.SLEEPING,
        ):

            self.orb.set_state(
                OrbState.LISTENING
            )

            self.status.setText(
                "STATUS  :  LISTENING"
            )

            self.bridge.request_voice_input()

        elif (
            self.orb.state
            == OrbState.LISTENING
        ):

            self.orb.set_state(
                OrbState.IDLE
            )

            self.status.setText(
                "STATUS  :  WAITING FOR COMMAND"
            )

    # ==================================================
    # JARVIS STATE
    # ==================================================

    def handle_state_change(
        self,
        state,
    ):

        try:

            orb_state = OrbState(
                state.lower()
            )

            self.orb.set_state(
                orb_state
            )

            self.status.setText(
                f"STATUS  :  {state.upper()}"
            )

            if (
                orb_state
                == OrbState.LISTENING
            ):

                self.microphone.start()

                self.show_wake_overlay()

            else:

                self.microphone.stop()

                self.overlay.hide_overlay()

        except ValueError:

            self.status.setText(
                f"STATUS  :  {state.upper()}"
            )

    # ==================================================
    # JARVIS RESPONSE
    # ==================================================

    def handle_jarvis_response(
        self,
        response,
    ):

        self.chat.add_jarvis_message(
            response
        )