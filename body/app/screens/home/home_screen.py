from pathlib import Path

from PySide6.QtCore import Qt, QSize
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
    QFrame,
    QSystemTrayIcon,
    QMenu,
    QStackedWidget,
    QToolButton,
)

from body.app.widgets.overlay import JarvisOverlay
from body.app.widgets.orb import OrbWidget, OrbState
from body.app.widgets.microphone import Microphone
from body.app.widgets.chrome_profile_selector import (
    ChromeProfileSelector,
)

from body.app.settings_manager import SettingsManager

from body.app.screens.settings.settings_screen import (
    SettingsScreen,
)

from body.app.screens.chat.chat_screen import (
    ChatScreen,
)

from bridge.bridge import JarvisBridge


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

        painter.setPen(
            QPen(
                marker_color,
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


# ============================================================
# MAIN WINDOW
# ============================================================


class MainWindow(QMainWindow):

    def __init__(
        self,
        bridge,
    ):
        super().__init__()

        # ========================================================
        # TRAY
        # ========================================================

        self.tray_icon = None
        self.tray_menu = None
        self._exiting = False

        # ========================================================
        # SETTINGS
        # ========================================================

        self.settings_manager = SettingsManager()

        # ========================================================
        # SCALE
        # ========================================================

        self.ui_scale = 1.0

        # ========================================================
        # WINDOW
        # ========================================================

        self.setWindowTitle(
            "J.A.R.V.I.S"
        )

        self.resize(
            1000,
            650,
        )

        # ========================================================
        # CENTRAL WIDGET
        # ========================================================

        self.central_widget = QWidget()

        self.setCentralWidget(
            self.central_widget
        )

        # ========================================================
        # BACKGROUND
        # ========================================================

        self.background = BackgroundFrame(
            self.central_widget
        )

        self.background.setGeometry(
            self.central_widget.rect()
        )

        self.background.lower()

        # ========================================================
        # PAGE STACK
        # ========================================================

        self.page_stack = QStackedWidget(
            self.central_widget
        )

        self.sidebar_width = 110

        self.page_stack.setGeometry(
            self.sidebar_width,
            0,
            max(
                1,
                self.central_widget.width()
                - self.sidebar_width,
            ),
            self.central_widget.height(),
        )

        # ========================================================
        # ORB PAGE
        # ========================================================

        self.home_page = QWidget()

        self.page_stack.addWidget(
            self.home_page
        )

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

        # ========================================================
        # HEADER
        # ========================================================

        self.header = QLabel(
            "J.A.R.V.I.S"
        )

        self.header.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.main_layout.addWidget(
            self.header,
            1,
        )

        # ========================================================
        # ORB
        # ========================================================

        self.orb = OrbWidget()

        self.main_layout.addWidget(
            self.orb,
            7,
        )

        # ========================================================
        # STATUS
        # ========================================================

        self.status = QLabel(
            "STATUS  :  WAITING FOR COMMAND"
        )

        self.status.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.main_layout.addWidget(
            self.status,
            1,
        )

        # ========================================================
        # FOOTER
        # ========================================================

        self.footer = QLabel(
            "J.A.R.V.I.S  •  SYSTEM ONLINE"
        )

        self.footer.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.main_layout.addWidget(
            self.footer,
            1,
        )

        # ========================================================
        # HUD
        # ========================================================

        self.hud_frame = HUDFrame(
            self.central_widget
        )

        self.hud_frame.setGeometry(
            self.central_widget.rect()
        )

        self.hud_frame.raise_()

        # ========================================================
        # MICROPHONE
        # ========================================================

        self.microphone = Microphone()

        # ========================================================
        # BRIDGE
        # ========================================================

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

        # ========================================================
        # OVERLAY
        # ========================================================

        self.overlay = JarvisOverlay()

        self.bridge.wake_detected.connect(
            self.show_wake_overlay
        )

        # ========================================================
        # MICROPHONE → ORB
        # ========================================================

        self.microphone.level_changed.connect(
            self.orb.set_audio_level
        )

        # ========================================================
        # MICROPHONE → OVERLAY
        # ========================================================

        self.microphone.level_changed.connect(
            self.overlay.set_audio_level
        )

        # ========================================================
        # ORB CLICK
        # ========================================================

        self.orb.clicked.connect(
            self.toggle_listening
        )

        self.orb.set_state(
            OrbState.IDLE
        )

        # ========================================================
        # PROFILE SELECTOR
        # ========================================================

        self.profile_selector = None

        # ========================================================
        # CHAT PAGE
        # ========================================================

        self.chat_screen = ChatScreen()

        self.chat_screen.chat_input.message_sent.connect(
            self.handle_text_message
        )

        self.page_stack.addWidget(
            self.chat_screen
        )

        # ========================================================
        # CHAT COMPATIBILITY ALIAS
        # ========================================================

        self.chat = self.chat_screen.conversation

        # ========================================================
        # SETTINGS PAGE
        # ========================================================

        self.settings_screen = SettingsScreen(
            self.settings_manager,
            self,
        )

        self.page_stack.addWidget(
            self.settings_screen
        )

        self.settings_screen.theme_changed.connect(
            self.apply_theme
        )

        # ========================================================
        # SIDEBAR
        # ========================================================

        self.sidebar = QFrame(
            self.central_widget
        )

        self.sidebar.setObjectName(
            "sidebar"
        )

        self.sidebar.setGeometry(
            0,
            0,
            self.sidebar_width,
            self.central_widget.height(),
        )

        self.sidebar_layout = QVBoxLayout(
            self.sidebar
        )

        self.sidebar_layout.setContentsMargins(
            10,
            18,
            10,
            18,
        )

        self.sidebar_layout.setSpacing(
            12
        )

        # ========================================================
        # SIDEBAR BRAND
        # ========================================================

        self.sidebar_brand = QLabel(
            "J.A.R.V.I.S"
        )

        self.sidebar_brand.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.sidebar_layout.addWidget(
            self.sidebar_brand
        )

        self.sidebar_layout.addSpacing(
            25
        )

        # ========================================================
        # SIDEBAR BUTTON CONSTANTS
        # ========================================================

        self.nav_button_size = 52
        self.nav_icon_size = 30

        # ========================================================
        # ORB NAV
        # ========================================================

        self.orb_nav_button = QToolButton()

        self.orb_nav_button.setToolTip(
            "Orb"
        )

        self.orb_nav_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.orb_nav_button.setFixedSize(
            self.nav_button_size,
            self.nav_button_size,
        )

        self.orb_nav_button.setText(
            "◉"
        )

        self.orb_nav_button.clicked.connect(
            self.show_home_page
        )

        self.sidebar_layout.addWidget(
            self.orb_nav_button,
            0,
            Qt.AlignmentFlag.AlignHCenter,
        )

        # ========================================================
        # CHAT NAV
        # ========================================================

        self.chat_nav_button = QToolButton()

        self.chat_nav_button.setToolTip(
            "Conversation"
        )

        self.chat_nav_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.chat_nav_button.setFixedSize(
            self.nav_button_size,
            self.nav_button_size,
        )

        self.chat_nav_button.setIconSize(
            QSize(
                self.nav_icon_size,
                self.nav_icon_size,
            )
        )

        # --------------------------------------------------------
        # CHAT PNG
        # --------------------------------------------------------

        chat_icon_path = (
            Path(__file__).resolve()
            .parents[2]
            / "assets"
            / "icons"
            / "chat_icon.png"
        )

        chat_pixmap = QPixmap(
            str(chat_icon_path)
        )

        if not chat_pixmap.isNull():

            chat_colored = QPixmap(
                chat_pixmap.size()
            )

            chat_colored.fill(
                Qt.GlobalColor.transparent
            )

            chat_painter = QPainter(
                chat_colored
            )

            chat_painter.setRenderHint(
                QPainter.RenderHint.Antialiasing
            )

            chat_painter.setCompositionMode(
                QPainter.CompositionMode.CompositionMode_SourceIn
            )

            chat_painter.fillRect(
                chat_colored.rect(),
                QColor(
                    "#00D9FF"
                ),
            )

            chat_painter.end()

            self.chat_nav_button.setIcon(
                QIcon(
                    chat_colored
                )
            )

        self.chat_nav_button.clicked.connect(
            self.show_chat_page
        )

        self.sidebar_layout.addWidget(
            self.chat_nav_button,
            0,
            Qt.AlignmentFlag.AlignHCenter,
        )

        # ========================================================
        # SETTINGS NAV
        # ========================================================

        self.settings_nav_button = QToolButton()

        self.settings_nav_button.setToolTip(
            "Settings"
        )

        self.settings_nav_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.settings_nav_button.setFixedSize(
            self.nav_button_size,
            self.nav_button_size,
        )

        self.settings_nav_button.setText(
            "⚙"
        )

        self.settings_nav_button.clicked.connect(
            self.show_settings_page
        )

        self.sidebar_layout.addWidget(
            self.settings_nav_button,
            0,
            Qt.AlignmentFlag.AlignHCenter,
        )

        self.sidebar_layout.addStretch()

        # ========================================================
        # APPLY THEME
        # ========================================================

        self.apply_theme(
            self.settings_manager.theme
        )

        # ========================================================
        # INITIAL PAGE
        # ========================================================

        self.show_home_page()

        # ========================================================
        # TRAY
        # ========================================================

        self.setup_system_tray()

        # ========================================================
        # SCALE
        # ========================================================

        self.update_ui_scale()

    # ============================================================
    # TRAY
    # ============================================================

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

    # ============================================================
    # TRAY RESTORE
    # ============================================================

    def restore_from_tray(
        self,
    ):

        self.show()
        self.showNormal()
        self.raise_()
        self.activateWindow()

    # ============================================================
    # TRAY LISTEN
    # ============================================================

    def start_listening_from_tray(
        self,
    ):

        self.restore_from_tray()

        if self.orb.state in (
            OrbState.IDLE,
            OrbState.SLEEPING,
        ):

            self.toggle_listening()

    # ============================================================
    # TRAY ACTIVATION
    # ============================================================

    def handle_tray_activation(
        self,
        reason,
    ):

        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):

            self.restore_from_tray()

    # ============================================================
    # CLOSE
    # ============================================================

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

    # ============================================================
    # EXIT
    # ============================================================

    def exit_from_tray(
        self,
    ):

        self._exiting = True

        if self.tray_icon is not None:

            self.tray_icon.hide()

        QApplication.quit()

    # ============================================================
    # NAVIGATION
    # ============================================================

    def set_active_nav(
        self,
        active_button,
    ):

        buttons = (
            self.orb_nav_button,
            self.chat_nav_button,
            self.settings_nav_button,
        )

        for button in buttons:

            button.setProperty(
                "active",
                button is active_button,
            )

            button.style().unpolish(
                button
            )

            button.style().polish(
                button
            )

            button.update()

    def show_home_page(
        self,
    ):

        self.page_stack.setCurrentWidget(
            self.home_page
        )

        self.set_active_nav(
            self.orb_nav_button
        )

    def show_chat_page(
        self,
    ):

        self.page_stack.setCurrentWidget(
            self.chat_screen
        )

        self.set_active_nav(
            self.chat_nav_button
        )

    def show_settings_page(
        self,
    ):

        self.page_stack.setCurrentWidget(
            self.settings_screen
        )

        self.set_active_nav(
            self.settings_nav_button
        )

    # ============================================================
    # THEME
    # ============================================================

    def apply_theme(
        self,
        theme,
    ):

        theme = theme.lower()

        # ========================================================
        # ORB
        # ========================================================

        if hasattr(
            self,
            "orb",
        ):

            self.orb.set_theme(
                theme
            )

        # ========================================================
        # CHAT SCREEN
        # ========================================================

        if hasattr(
            self,
            "chat_screen",
        ):

            self.chat_screen.apply_theme(
                theme
            )

        # ========================================================
        # SETTINGS
        # ========================================================

        if hasattr(
            self,
            "settings_screen",
        ):

            self.settings_screen.apply_theme(
                theme
            )

        # ========================================================
        # BACKGROUND
        # ========================================================

        if hasattr(
            self,
            "background",
        ):

            self.background.set_theme(
                theme
            )

        # ========================================================
        # HUD
        # ========================================================

        if hasattr(
            self,
            "hud_frame",
        ):

            self.hud_frame.set_theme(
                theme
            )

        # ========================================================
        # MAIN WINDOW
        # ========================================================

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

        # ========================================================
        # SIDEBAR
        # ========================================================

        if hasattr(
            self,
            "sidebar",
        ):

            self.update_sidebar_style()

        # ========================================================
        # SCALE
        # ========================================================

        self.update_ui_scale()

    # ============================================================
    # SIDEBAR STYLE
    # ============================================================

    def update_sidebar_style(
        self,
    ):

        theme = self.settings_manager.theme.lower()

        if theme == "light":

            self.sidebar.setStyleSheet(
                """
                QFrame#sidebar {
                    background: #DCEFF4;
                    border-right: 1px solid #69B5C9;
                }

                QLabel {
                    background: transparent;
                    color: #08202C;
                    font-size: 11px;
                    font-weight: 700;
                    letter-spacing: 2px;
                }

                QToolButton {
                    background: transparent;
                    color: #477B8C;
                    border: 1px solid transparent;
                    border-radius: 9px;
                }

                QToolButton:hover {
                    background: #C8EAF2;
                    color: #008FB8;
                    border: 1px solid #69B5C9;
                }

                QToolButton[active="true"] {
                    background: #C2EAF3;
                    color: #008FB8;
                    border: 1px solid #00A8D6;
                }
                """
            )

        else:

            self.sidebar.setStyleSheet(
                """
                QFrame#sidebar {
                    background: #020912;
                    border-right: 1px solid #16445A;
                }

                QLabel {
                    background: transparent;
                    color: #DDEFFF;
                    font-size: 11px;
                    font-weight: 700;
                    letter-spacing: 2px;
                }

                QToolButton {
                    background: transparent;
                    color: #5C91B5;
                    border: 1px solid transparent;
                    border-radius: 9px;
                }

                QToolButton:hover {
                    background: #061B28;
                    color: #00D9FF;
                    border: 1px solid #126486;
                }

                QToolButton[active="true"] {
                    background: #062638;
                    color: #00D9FF;
                    border: 1px solid #00D9FF;
                }
                """
            )

    # ============================================================
    # RESPONSIVE SCALE
    # ============================================================

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

        # ========================================================
        # HEADER
        # ========================================================

        header_size = max(
            18,
            int(
                27 * scale
            ),
        )

        header_spacing = max(
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
                font-family:
                    "Orbitron",
                    "Eurostile",
                    "Arial";
                font-size: {header_size}px;
                font-weight: 700;
                letter-spacing: {header_spacing}px;
            }}
            """
        )

        # ========================================================
        # STATUS
        # ========================================================

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
                font-family:
                    "Orbitron",
                    "Eurostile",
                    "Arial";
                font-size: {status_size}px;
                font-weight: 600;
                letter-spacing: {status_spacing}px;
            }}
            """
        )

        # ========================================================
        # FOOTER
        # ========================================================

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
                font-family:
                    "Orbitron",
                    "Eurostile",
                    "Arial";
                font-size: {footer_size}px;
                font-weight: 600;
                letter-spacing: {footer_spacing}px;
            }}
            """
        )

        # ========================================================
        # ORB PAGE
        # ========================================================

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

        # ========================================================
        # SIDEBAR
        # ========================================================

        if hasattr(
            self,
            "sidebar",
        ):

            self.sidebar.setGeometry(
                0,
                0,
                self.sidebar_width,
                self.central_widget.height(),
            )

            nav_size = max(
                44,
                int(
                    52 * scale
                ),
            )

            icon_size = max(
                24,
                int(
                    30 * scale
                ),
            )

            sidebar_font = max(
                18,
                int(
                    23 * scale
                ),
            )

            for button in (
                self.orb_nav_button,
                self.chat_nav_button,
                self.settings_nav_button,
            ):

                button.setFixedSize(
                    nav_size,
                    nav_size,
                )

                button.setIconSize(
                    QSize(
                        icon_size,
                        icon_size,
                    )
                )

                button.setStyleSheet(
                    f"""
                    QToolButton {{
                        background: transparent;
                        color: #5C91B5;
                        border: 1px solid transparent;
                        border-radius: 9px;
                        font-size: {sidebar_font}px;
                    }}

                    QToolButton:hover {{
                        background: #061B28;
                        color: #00D9FF;
                        border: 1px solid #126486;
                    }}

                    QToolButton[active="true"] {{
                        background: #062638;
                        color: #00D9FF;
                        border: 1px solid #00D9FF;
                    }}
                    """
                )

            self.sidebar_brand.setStyleSheet(
                f"""
                QLabel {{
                    background: transparent;
                    color: #DDEFFF;
                    font-size: {max(9, int(11 * scale))}px;
                    font-weight: 700;
                    letter-spacing: {max(1, int(2 * scale))}px;
                }}
                """
            )

            if self.settings_manager.theme.lower() == "light":

                for button in (
                    self.orb_nav_button,
                    self.chat_nav_button,
                    self.settings_nav_button,
                ):

                    button.setStyleSheet(
                        f"""
                        QToolButton {{
                            background: transparent;
                            color: #477B8C;
                            border: 1px solid transparent;
                            border-radius: 9px;
                            font-size: {sidebar_font}px;
                        }}

                        QToolButton:hover {{
                            background: #C8EAF2;
                            color: #008FB8;
                            border: 1px solid #69B5C9;
                        }}

                        QToolButton[active="true"] {{
                            background: #C2EAF3;
                            color: #008FB8;
                            border: 1px solid #00A8D6;
                        }}
                        """
                    )

                self.sidebar_brand.setStyleSheet(
                    f"""
                    QLabel {{
                        background: transparent;
                        color: #08202C;
                        font-size: {max(9, int(11 * scale))}px;
                        font-weight: 700;
                        letter-spacing: {max(1, int(2 * scale))}px;
                    }}
                    """
                )

    # ============================================================
    # RESIZE
    # ============================================================

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
            "sidebar",
        ):

            self.sidebar.setGeometry(
                0,
                0,
                self.sidebar_width,
                self.central_widget.height(),
            )

        if hasattr(
            self,
            "page_stack",
        ):

            self.page_stack.setGeometry(
                self.sidebar_width,
                0,
                max(
                    1,
                    self.central_widget.width()
                    - self.sidebar_width,
                ),
                self.central_widget.height(),
            )

        self.update_ui_scale()

    # ============================================================
    # TEXT MESSAGE
    # ============================================================

    def handle_text_message(
        self,
        message,
    ):

        self.chat_screen.conversation.add_user_message(
            message
        )

        self.bridge.send_command(
            message
        )

    # ============================================================
    # PROFILE SELECTION
    # ============================================================

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

    # ============================================================
    # PROFILE SELECTED
    # ============================================================

    def handle_profile_selected(
        self,
        profile_directory,
    ):

        self.bridge.send_profile_selection(
            profile_directory
        )

    # ============================================================
    # WAKE OVERLAY
    # ============================================================

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

        if self.settings_manager.overlay_enabled:

            self.overlay.show_overlay()

    # ============================================================
    # TOGGLE LISTENING
    # ============================================================

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

    # ============================================================
    # JARVIS STATE
    # ============================================================

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

    # ============================================================
    # JARVIS RESPONSE
    # ============================================================

    def handle_jarvis_response(
        self,
        response,
    ):

        self.chat_screen.conversation.add_jarvis_message(
            response
        )