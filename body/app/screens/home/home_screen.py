from pathlib import Path

import numpy as np

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import (
    QPainter,
    QPen,
    QColor,
    QIcon,
    QPixmap,
    QImage,
)
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QVBoxLayout,
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
from body.app.widgets.background_frame import (
    BackgroundFrame,
)
from body.app.widgets.hud_frame import (
    HUDFrame,
)

from body.app.settings_manager import SettingsManager

from body.app.utils.helpers import (
    qimage_to_channels,
    alpha_plane_to_qimage,
    grayscale8_roundtrip,
)

from body.app.screens.settings.settings_screen import (
    SettingsScreen,
)

from body.app.screens.chat.chat_screen import (
    ChatScreen,
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
        self._last_scale = None

        self.current_theme = (
            self.settings_manager.theme.lower()
        )

        # ========================================================
        # ICON CACHE
        # ========================================================

        self._chat_icons = {}
        self._orb_icons = {}

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

        # Compatibility alias used elsewhere.
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

        # Overlay setting must update the running application.
        if hasattr(
            self.settings_screen,
            "overlay_checkbox",
        ):
            self.settings_screen.overlay_checkbox.toggled.connect(
                self.handle_overlay_setting_changed
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

        self.sidebar_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
            | Qt.AlignmentFlag.AlignHCenter
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

        self.sidebar_brand.setMinimumWidth(
            self.sidebar_width - 20
        )

        self.sidebar_brand.setMaximumWidth(
            self.sidebar_width - 20
        )

        self.sidebar_layout.addWidget(
            self.sidebar_brand,
            0,
            Qt.AlignmentFlag.AlignHCenter,
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

        self.orb_icon_path = (
            Path(__file__).resolve()
            .parents[2]
            / "assets"
            / "icons"
            / "orb_icon.png"
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

        self.chat_icon_path = (
            Path(__file__).resolve()
            .parents[2]
            / "assets"
            / "icons"
            / "chat_icon.png"
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
        # INITIAL ICON GENERATION
        # ========================================================

        self.update_chat_icon_theme(
            self.current_theme
        )

        self.update_orb_icon_theme(
            self.current_theme
        )

        # ========================================================
        # APPLY THEME
        # ========================================================

        self.apply_theme(
            self.current_theme
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

        self.update_ui_scale(
            force=True
        )

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
    # CHAT ICON THEME
    # ============================================================

    def update_chat_icon_theme(
        self,
        theme,
    ):

        if not hasattr(
            self,
            "chat_nav_button",
        ):
            return

        theme = theme.lower()

        if theme in self._chat_icons:
            self.chat_nav_button.setIcon(
                self._chat_icons[theme]
            )
            return

        icon_color = QColor(
            "#008FB8"
            if theme == "light"
            else "#00D9FF"
        )

        source = QImage(
            str(self.chat_icon_path)
        )

        if source.isNull():
            print(
                "JARVIS: ERROR - Chat icon could not be loaded:",
                self.chat_icon_path,
            )
            return

        # Work on a tiny cached raster. The sidebar icon is only
        # around 30 px, so processing a 256 px source is more than
        # enough and avoids UI freezes during theme changes.
        source = source.scaled(
            256,
            256,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,
        ).convertToFormat(
            QImage.Format.Format_ARGB32
        )

        colored = self.recolor_chat_pixels(
            source,
            icon_color,
        )

        if colored is None:
            return

        icon = QIcon(
            QPixmap.fromImage(colored)
        )

        self._chat_icons[theme] = icon
        self.chat_nav_button.setIcon(icon)

    # ============================================================
    # ORB ICON THEME
    # ============================================================

    def update_orb_icon_theme(
        self,
        theme,
    ):

        if not hasattr(
            self,
            "orb_nav_button",
        ):
            return

        theme = theme.lower()

        if theme in self._orb_icons:
            self.orb_nav_button.setIcon(
                self._orb_icons[theme]
            )
            return

        # The light theme uses a deliberately darker cyan so the
        # supplied Orb artwork does not disappear into the light UI.
        icon_color = QColor(
            "#00536B"
            if theme == "light"
            else "#00D9FF"
        )

        source = QImage(
            str(self.orb_icon_path)
        )

        if source.isNull():
            print(
                "JARVIS: ERROR - Orb icon could not be loaded:",
                self.orb_icon_path,
            )
            return

        # Downsample BEFORE pixel analysis. The original artwork is
        # large, but the sidebar icon is small. This removes the
        # several-million-pixel processing delay on theme changes.
        source = source.scaled(
            256,
            256,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,
        ).convertToFormat(
            QImage.Format.Format_ARGB32
        )

        colored = self.recolor_orb_pixels(
            source,
            icon_color,
        )

        if colored is None:
            return

        icon = QIcon(
            QPixmap.fromImage(colored)
        )

        self._orb_icons[theme] = icon
        self.orb_nav_button.setIcon(icon)

    # ============================================================
    # ICON RECOLOURING
    # ============================================================
    #
    # Both icons are recoloured with exactly the integer arithmetic they
    # always used. The only change is that numpy applies it to the whole
    # array at once instead of running one Python iteration per pixel,
    # which was around 65,000 iterations per icon per theme.
    #
    # The original loops are kept below as a fallback, so a numpy or Qt
    # buffer problem can only ever cost speed, never correctness.
    # ============================================================

    def recolor_chat_pixels(
        self,
        source,
        icon_color,
    ):
        """
        Tint the chat icon, deriving each pixel's alpha from how dark it
        is. Returns an ARGB32 QImage, or None if the source is unusable.
        """

        red = icon_color.red()
        green = icon_color.green()
        blue = icon_color.blue()

        try:

            channels = qimage_to_channels(
                source
            )

            if channels is None:
                return None

            alpha, r, g, b = channels

            luminance = (
                299 * r +
                587 * g +
                114 * b
            ) // 1000

            darkness = 255 - luminance
            final_alpha = (alpha * darkness) // 255

            # Transparent source pixels and near-invisible results are
            # discarded, exactly as the original loop discarded them.
            final_alpha[
                (alpha == 0)
                | (final_alpha < 8)
            ] = 0

            return alpha_plane_to_qimage(
                final_alpha,
                red,
                green,
                blue,
            )

        except Exception as error:

            print(
                "JARVIS: ERROR - Chat icon recolour failed:",
                error,
            )

            return None

    # ============================================================

    def recolor_orb_pixels(
        self,
        source,
        icon_color,
    ):
        """
        Tint the orb icon and crop it to its artwork.

        The mask keeps saturated colour and dark linework while rejecting
        the pale checkerboard background baked into the source PNG. What
        survives is then cropped to its bounding box, plus a small pad.
        """

        red = icon_color.red()
        green = icon_color.green()
        blue = icon_color.blue()

        try:

            channels = qimage_to_channels(
                source
            )

            if channels is None:
                return None

            alpha, r, g, b = channels

            maximum = np.maximum(
                np.maximum(r, g),
                b,
            )

            minimum = np.minimum(
                np.minimum(r, g),
                b,
            )

            saturation = maximum - minimum

            luminance = (
                299 * r +
                587 * g +
                114 * b
            ) // 1000

            color_alpha = np.minimum(
                255,
                saturation * 6,
            )

            dark_alpha = np.clip(
                (175 - luminance) * 5,
                0,
                255,
            )

            final_alpha = np.maximum(
                color_alpha,
                dark_alpha,
            )

            keep = (
                (alpha != 0)
                & (
                    (saturation >= 18)
                    | (luminance <= 155)
                )
                & (final_alpha >= 25)
            )

            mask = np.where(
                keep,
                grayscale8_roundtrip(final_alpha),
                0,
            )

            # ================================================
            # FOREGROUND BOUNDING BOX
            # ================================================

            rows = np.flatnonzero(
                keep.any(axis=1)
            )

            columns = np.flatnonzero(
                keep.any(axis=0)
            )

            if (
                rows.size == 0
                or columns.size == 0
            ):
                print(
                    "JARVIS: ERROR - Orb icon foreground could not be detected:",
                    self.orb_icon_path,
                )
                return None

            height, width = keep.shape

            padding = max(
                2,
                int(
                    min(width, height) * 0.015
                ),
            )

            min_x = max(
                0,
                int(columns[0]) - padding,
            )

            min_y = max(
                0,
                int(rows[0]) - padding,
            )

            max_x = min(
                width - 1,
                int(columns[-1]) + padding,
            )

            max_y = min(
                height - 1,
                int(rows[-1]) + padding,
            )

            cropped = mask[
                min_y : max_y + 1,
                min_x : max_x + 1,
            ]

            return alpha_plane_to_qimage(
                cropped,
                red,
                green,
                blue,
            )

        except Exception as error:

            print(
                "JARVIS: ERROR - Orb icon recolour failed:",
                error,
            )

            return None

    # ============================================================
    # THEME
    # ============================================================

    def apply_theme(
        self,
        theme,
    ):

        theme = theme.lower()

        self.current_theme = theme

        # ========================================================
        # ICONS
        # ========================================================

        self.update_chat_icon_theme(
            theme
        )

        self.update_orb_icon_theme(
            theme
        )

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
        # SIDEBAR STYLE
        # ========================================================

        if hasattr(
            self,
            "sidebar",
        ):

            self.update_sidebar_style(
                theme
            )

        # ========================================================
        # SCALE
        # ========================================================

        self.update_ui_scale(
            force=True
        )

    # ============================================================
    # SIDEBAR STYLE
    # ============================================================

    def update_sidebar_style(
        self,
        theme=None,
    ):

        theme = (
            theme
            or self.current_theme
            or self.settings_manager.theme
        ).lower()

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
        force=False,
    ):

        width = max(1, self.width())
        height = max(1, self.height())

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

        # Do not repeatedly rebuild stylesheets while Qt is emitting
        # several resize events during maximize/minimize.
        if (
            not force
            and self._last_scale is not None
            and abs(scale - self._last_scale) < 0.01
        ):
            return

        self._last_scale = scale
        self.ui_scale = scale

        # ========================================================
        # HEADER
        # ========================================================

        header_size = max(
            18,
            int(27 * scale),
        )

        header_spacing = max(
            2,
            int(8 * scale),
        )

        header_color = (
            "#08202C"
            if self.current_theme == "light"
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
            int(11 * scale),
        )

        status_spacing = max(
            1,
            int(2 * scale),
        )

        status_color = (
            "#26728A"
            if self.current_theme == "light"
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
            int(10 * scale),
        )

        footer_spacing = max(
            1,
            int(3 * scale),
        )

        footer_color = (
            "#47849A"
            if self.current_theme == "light"
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
        # ORB PAGE LAYOUT
        # ========================================================

        self.main_layout.setContentsMargins(
            max(24, int(38 * scale)),
            max(18, int(28 * scale)),
            max(24, int(38 * scale)),
            max(18, int(24 * scale)),
        )

        self.main_layout.setSpacing(
            max(6, int(10 * scale))
        )

        # ========================================================
        # SIDEBAR
        # ========================================================

        if hasattr(self, "sidebar"):

            self.sidebar.setGeometry(
                0,
                0,
                self.sidebar_width,
                self.central_widget.height(),
            )

            nav_size = max(
                44,
                int(52 * scale),
            )

            icon_size = max(
                24,
                int(30 * scale),
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

            # The Settings icon is a glyph, so it must be scaled
            # independently from PNG icons.
            settings_font = max(
                18,
                int(23 * scale),
            )

            if self.current_theme == "light":
                normal = "#477B8C"
                hover_bg = "#C8EAF2"
                hover = "#008FB8"
                hover_border = "#69B5C9"
                active_bg = "#C2EAF3"
                active = "#008FB8"
                active_border = "#00A8D6"
            else:
                normal = "#5C91B5"
                hover_bg = "#061B28"
                hover = "#00D9FF"
                hover_border = "#126486"
                active_bg = "#062638"
                active = "#00D9FF"
                active_border = "#00D9FF"

            for button in (
                self.orb_nav_button,
                self.chat_nav_button,
            ):
                button.setStyleSheet(
                    f"""
                    QToolButton {{
                        background: transparent;
                        color: {normal};
                        border: 1px solid transparent;
                        border-radius: 9px;
                    }}

                    QToolButton:hover {{
                        background: {hover_bg};
                        color: {hover};
                        border: 1px solid {hover_border};
                    }}

                    QToolButton[active="true"] {{
                        background: {active_bg};
                        color: {active};
                        border: 1px solid {active_border};
                    }}
                    """
                )

            self.settings_nav_button.setStyleSheet(
                f"""
                QToolButton {{
                    background: transparent;
                    color: {normal};
                    border: 1px solid transparent;
                    border-radius: 9px;
                    font-size: {settings_font}px;
                    font-family: "Segoe UI Symbol", "Segoe UI", Arial;
                    padding: 0px;
                }}

                QToolButton:hover {{
                    background: {hover_bg};
                    color: {hover};
                    border: 1px solid {hover_border};
                }}

                QToolButton[active="true"] {{
                    background: {active_bg};
                    color: {active};
                    border: 1px solid {active_border};
                }}
                """
            )

            # Keep the brand safely inside the 110 px sidebar even
            # at small window sizes. No clipping of J.A.R.V.I.S.
            brand_font = max(
                7,
                min(
                    10,
                    int(10 * scale),
                ),
            )

            brand_spacing = max(
                1,
                min(
                    2,
                    int(2 * scale),
                ),
            )

            self.sidebar_brand.setMinimumWidth(
                self.sidebar_width - 20
            )
            self.sidebar_brand.setMaximumWidth(
                self.sidebar_width - 20
            )
            self.sidebar_brand.setMinimumHeight(24)

            brand_color = (
                "#08202C"
                if self.current_theme == "light"
                else "#DDEFFF"
            )

            self.sidebar_brand.setStyleSheet(
                f"""
                QLabel {{
                    background: transparent;
                    color: {brand_color};
                    font-family:
                        "Orbitron",
                        "Eurostile",
                        "Arial";
                    font-size: {brand_font}px;
                    font-weight: 700;
                    letter-spacing: {brand_spacing}px;
                    padding: 0px;
                    margin: 0px;
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

        # Resize only updates geometry/font/icon display sizes.
        # PNG processing is cached and never happens here.
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
    # OVERLAY SETTING
    # ============================================================

    def handle_overlay_setting_changed(
        self,
        enabled,
    ):

        enabled = bool(
            enabled
        )

        try:

            self.settings_manager.overlay_enabled = enabled

        except (
            AttributeError,
            TypeError,
        ):

            pass

        if not enabled:

            self.overlay.hide_overlay()

            return

        if self.orb.state == OrbState.LISTENING:

            self.show_wake_overlay()

    # ============================================================
    # WAKE OVERLAY
    # ============================================================

    def show_wake_overlay(
        self,
    ):

        if not self.settings_manager.overlay_enabled:

            self.overlay.hide_overlay()

            return

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