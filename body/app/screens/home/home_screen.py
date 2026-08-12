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
    QWidget,
    QSystemTrayIcon,
    QMenu,
)

from body.app.widgets.overlay import JarvisOverlay
from body.app.widgets.orb import OrbWidget, OrbState
from body.app.widgets.microphone import Microphone
from body.app.widgets.conversation import ConversationWidget
from body.app.widgets.chat_input import ChatInput
from body.app.widgets.chrome_profile_selector import (
    ChromeProfileSelector,
)

from bridge.bridge import JarvisBridge


# ==================================================
# BACKGROUND
# ==================================================


class BackgroundFrame(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        width = self.width()
        height = self.height()

        center_x = width // 2
        center_y = int(height * 0.35)

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
            QColor(1, 5, 10),
        )

        base_gradient.setColorAt(
            0.5,
            QColor(2, 9, 17),
        )

        base_gradient.setColorAt(
            1.0,
            QColor(0, 4, 9),
        )

        painter.fillRect(
            self.rect(),
            base_gradient,
        )

        # ==========================================
        # CENTRAL BLUE GLOW
        # ==========================================

        glow = QRadialGradient(
            center_x,
            center_y,
            min(width, height) * 0.48,
        )

        glow.setColorAt(
            0.0,
            QColor(0, 90, 140, 32),
        )

        glow.setColorAt(
            0.30,
            QColor(0, 55, 100, 20),
        )

        glow.setColorAt(
            0.65,
            QColor(0, 25, 55, 8),
        )

        glow.setColorAt(
            1.0,
            QColor(0, 0, 0, 0),
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
            QColor(0, 0, 0, 0),
        )

        horizontal_glow.setColorAt(
            0.35,
            QColor(0, 110, 170, 10),
        )

        horizontal_glow.setColorAt(
            0.5,
            QColor(0, 160, 220, 18),
        )

        horizontal_glow.setColorAt(
            0.65,
            QColor(0, 110, 170, 10),
        )

        horizontal_glow.setColorAt(
            1.0,
            QColor(0, 0, 0, 0),
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

        circuit_pen = QPen(
            QColor(
                0,
                110,
                170,
                30,
            ),
            1,
        )

        painter.setPen(
            circuit_pen
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

        side_pen = QPen(
            QColor(
                0,
                130,
                190,
                24,
            ),
            1,
        )

        painter.setPen(
            side_pen
        )

        # LEFT
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

        # RIGHT
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
        # SMALL DATA TICKS
        # ==========================================

        tick_pen = QPen(
            QColor(
                0,
                160,
                220,
                35,
            ),
            1,
        )

        painter.setPen(
            tick_pen
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

        dot_pen = QPen(
            QColor(
                0,
                180,
                240,
                65,
            ),
            2,
        )

        painter.setPen(
            dot_pen
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
        # SUBTLE CIRCULAR HUD RINGS
        # ==========================================

        ring_pen = QPen(
            QColor(
                0,
                120,
                180,
                15,
            ),
            1,
        )

        painter.setPen(
            ring_pen
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

        top_pen = QPen(
            QColor(
                0,
                150,
                210,
                40,
            ),
            1,
        )

        painter.setPen(
            top_pen
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

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        width = self.width()
        height = self.height()

        # ==========================================
        # HUD FRAME
        # ==========================================

        pen = QPen(
            QColor(
                0,
                150,
                210,
                75,
            ),
            1,
        )

        painter.setPen(
            pen
        )

        margin = 8
        corner = 28

        # ==========================================
        # TOP LEFT
        # ==========================================

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

        # ==========================================
        # TOP RIGHT
        # ==========================================

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

        # ==========================================
        # BOTTOM LEFT
        # ==========================================

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

        # ==========================================
        # BOTTOM RIGHT
        # ==========================================

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

        marker_pen = QPen(
            QColor(
                0,
                217,
                255,
                45,
            ),
            1,
        )

        painter.setPen(
            marker_pen
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
        # SMALL HUD TICKS
        # ==========================================

        tick_color = QColor(
            0,
            217,
            255,
            65,
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

    def __init__(self, bridge):
        super().__init__()

        # ==========================================
        # SYSTEM TRAY
        # ==========================================

        self.tray_icon = None
        self.tray_menu = None
        self._exiting = False

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
        # MAIN WINDOW STYLE
        # ==========================================

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

        # ==========================================
        # CENTRAL WIDGET
        # ==========================================

        self.central_widget = QWidget()

        self.central_widget.setStyleSheet(
            """
            QWidget {
                background: transparent;
            }
            """
        )

        self.setCentralWidget(
            self.central_widget
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

        self.main_layout = QVBoxLayout()

        self.main_layout.setContentsMargins(
            38,
            28,
            38,
            24,
        )

        self.main_layout.setSpacing(
            10
        )

        self.central_widget.setLayout(
            self.main_layout
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
        # WAKE WORD OVERLAY
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

        # ==========================================
        # INITIAL ORB STATE
        # ==========================================

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
        # ADD WIDGETS
        # ==========================================

        self.main_layout.addWidget(
            self.header,
            1,
        )

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
        # SYSTEM TRAY
        # ==========================================

        self.setup_system_tray()

    # ==================================================
    # SYSTEM TRAY SETUP
    # ==================================================

    def setup_system_tray(self):

        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        # ==========================================
        # CREATE TRAY ICON
        # ==========================================

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

        # Outer orb
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

        # Inner orb
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

        # ==========================================
        # TRAY MENU
        # ==========================================

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

        # ==========================================
        # TRAY ACTIVATION
        # ==========================================

        self.tray_icon.activated.connect(
            self.handle_tray_activation
        )

        self.tray_icon.show()

    # ==================================================
    # RESTORE FROM TRAY
    # ==================================================

    def restore_from_tray(self):

        self.show()
        self.showNormal()
        self.raise_()
        self.activateWindow()

    # ==================================================
    # START LISTENING FROM TRAY
    # ==================================================

    def start_listening_from_tray(self):

        self.restore_from_tray()

        if self.orb.state in (
            OrbState.IDLE,
            OrbState.SLEEPING,
        ):

            self.toggle_listening()

    # ==================================================
    # HANDLE TRAY ACTIVATION
    # ==================================================

    def handle_tray_activation(
        self,
        reason,
    ):

        if (
            reason
            == QSystemTrayIcon.ActivationReason.Trigger
        ):

            self.restore_from_tray()

        elif (
            reason
            == QSystemTrayIcon.ActivationReason.DoubleClick
        ):

            self.restore_from_tray()

    # ==================================================
    # CLOSE WINDOW
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
    # EXIT FROM TRAY
    # ==================================================

    def exit_from_tray(self):

        self._exiting = True

        if self.tray_icon is not None:
            self.tray_icon.hide()

        QApplication.quit()

    # ==================================================
    # RESIZE HUD
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

    # ==================================================
    # HANDLE TEXT MESSAGE
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
    # HANDLE PROFILE SELECTION REQUEST
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
    # HANDLE SELECTED PROFILE
    # ==================================================

    def handle_profile_selected(
        self,
        profile_directory,
    ):

        self.bridge.send_profile_selection(
            profile_directory
        )

    # ==================================================
    # SHOW WAKE OVERLAY
    # ==================================================

    def show_wake_overlay(self):

        active_window = QApplication.activeWindow()

        # Keep the main JARVIS interface uncluttered.
        # The floating indicator is only useful when
        # the user is interacting with another app.

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

    def toggle_listening(self):

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
    # HANDLE JARVIS STATE
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

            # ==========================================
            # OVERLAY LIFECYCLE
            # ==========================================

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
    # HANDLE JARVIS RESPONSE
    # ==================================================

    def handle_jarvis_response(
        self,
        response,
    ):

        self.chat.add_jarvis_message(
            response
        )


# ==================================================
# END OF FILE
# ==================================================