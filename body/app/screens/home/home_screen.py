from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from body.app.widgets.orb import OrbWidget, OrbState
from body.app.widgets.microphone import Microphone
from body.app.widgets.conversation import ConversationWidget
from body.app.widgets.chat_input import ChatInput
from body.app.widgets.chrome_profile_selector import (
    ChromeProfileSelector,
)

from bridge.bridge import JarvisBridge


class MainWindow(QMainWindow):

    def __init__(self, bridge):
        super().__init__()

        self.setWindowTitle("JARVIS")
        self.resize(1000, 650)

        # ==========================================
        # CENTRAL WIDGET
        # ==========================================

        self.central_widget = QWidget()

        self.setCentralWidget(
            self.central_widget
        )

        # ==========================================
        # MAIN LAYOUT
        # ==========================================

        self.main_layout = QVBoxLayout()

        self.central_widget.setLayout(
            self.main_layout
        )

        # ==========================================
        # HEADER
        # ==========================================

        self.header = QLabel(
            "JARVIS"
        )

        self.header.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        # ==========================================
        # ORB
        # ==========================================

        self.orb = OrbWidget()

        # ==========================================
        # MICROPHONE
        # ==========================================

        self.microphone = Microphone()

        self.microphone.level_changed.connect(
            self.orb.set_audio_level
        )

        # ==========================================
        # ORB CLICK
        # ==========================================

        self.orb.clicked.connect(
            self.toggle_listening
        )

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
        # INITIAL STATE
        # ==========================================

        self.orb.set_state(
            OrbState.IDLE
        )

        # ==========================================
        # STATUS
        # ==========================================

        self.status = QLabel(
            "Status : Waiting for command..."
        )

        self.status.setAlignment(
            Qt.AlignmentFlag.AlignCenter
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
            "Version 0.1      |      Offline"
        )

        self.footer.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        # ==========================================
        # ADD WIDGETS
        # ==========================================

        self.main_layout.addWidget(
            self.header,
            1
        )

        self.main_layout.addWidget(
            self.orb,
            5
        )

        self.main_layout.addWidget(
            self.status,
            1
        )

        self.main_layout.addWidget(
            self.chat,
            3
        )

        self.main_layout.addWidget(
            self.chat_input
        )

        self.main_layout.addWidget(
            self.footer,
            1
        )

        # ==========================================
        # PROFILE SELECTOR
        # ==========================================

        self.profile_selector = None

    # ==================================================
    # HANDLE TEXT MESSAGE
    # ==================================================

    def handle_text_message(self, message):

        self.chat.add_user_message(
            message
        )

        self.bridge.send_command(
            message
        )

    # ==================================================
    # HANDLE PROFILE SELECTION REQUEST
    # ==================================================

    def handle_profile_selection(self, profiles):
        """
        Displays the Chrome profile selector
        when the Brain requests one.
        """

        self.profile_selector = (
            ChromeProfileSelector(
                profiles,
                self
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
        profile_directory
    ):
        """
        Sends the selected Chrome profile
        back to the Brain.
        """

        self.bridge.send_profile_selection(
            profile_directory
        )

    # ==================================================
    # TOGGLE LISTENING
    # ==================================================

    def toggle_listening(self):

        if self.orb.state == OrbState.IDLE:

            self.orb.set_state(
                OrbState.LISTENING
            )

            self.status.setText(
                "Status : Listening..."
            )

            self.microphone.start()

        elif self.orb.state == OrbState.LISTENING:

            self.microphone.stop()

            self.orb.set_state(
                OrbState.IDLE
            )

            self.status.setText(
                "Status : Waiting for command..."
            )

    # ==================================================
    # HANDLE JARVIS STATE
    # ==================================================

    def handle_state_change(self, state):

        try:

            orb_state = OrbState(
                state.lower()
            )

            self.orb.set_state(
                orb_state
            )

            self.status.setText(
                f"Status : {state.title()}"
            )

        except ValueError:

            self.status.setText(
                f"Status : Unknown state ({state})"
            )

    # ==================================================
    # HANDLE JARVIS RESPONSE
    # ==================================================

    def handle_jarvis_response(self, response):

        self.chat.add_jarvis_message(
            response
        )