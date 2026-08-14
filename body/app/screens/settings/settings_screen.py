from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QSlider,
    QCheckBox,
    QFrame,
)


class SettingsScreen(QWidget):

    back_requested = Signal()
    theme_changed = Signal(str)

    def __init__(
        self,
        settings_manager,
        parent=None,
    ):
        super().__init__(parent)

        self.settings_manager = settings_manager
        self._loading = False
        self.current_theme = "dark"

        self.build_ui()
        self.load_settings()

    # ==================================================
    # BUILD UI
    # ==================================================

    def build_ui(self):

        self.setObjectName(
            "settingsScreen"
        )

        self.layout_main = QVBoxLayout(self)

        self.layout_main.setContentsMargins(
            40,
            20,
            40,
            20,
        )

        self.layout_main.setSpacing(
            10
        )

        # ==========================================
        # TITLE
        # ==========================================

        self.title = QLabel(
            "SETTINGS"
        )

        self.title.setObjectName(
            "settingsTitle"
        )

        self.title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.layout_main.addWidget(
            self.title
        )

        # ==========================================
        # TITLE LINE
        # ==========================================

        self.title_line = QFrame()

        self.title_line.setFrameShape(
            QFrame.Shape.HLine
        )

        self.title_line.setObjectName(
            "separator"
        )

        self.layout_main.addWidget(
            self.title_line
        )

        # ==========================================
        # VOICE TITLE
        # ==========================================

        self.voice_title = QLabel(
            "VOICE"
        )

        self.voice_title.setProperty(
            "class",
            "sectionTitle",
        )

        self.layout_main.addWidget(
            self.voice_title
        )

        # ==========================================
        # VOICE PANEL
        # ==========================================

        self.voice_panel = QFrame()

        self.voice_panel.setObjectName(
            "settingPanel"
        )

        voice_layout = QVBoxLayout(
            self.voice_panel
        )

        voice_layout.setContentsMargins(
            18,
            10,
            18,
            10,
        )

        voice_layout.setSpacing(
            6
        )

        # ==========================================
        # MICROPHONE
        # ==========================================

        microphone_row = QHBoxLayout()

        self.microphone_label = QLabel(
            "Microphone"
        )

        self.microphone_label.setProperty(
            "class",
            "settingLabel",
        )

        self.microphone_combo = QComboBox()

        self.microphone_combo.addItem(
            "Default Microphone",
            -1,
        )

        microphone_row.addWidget(
            self.microphone_label
        )

        microphone_row.addStretch()

        microphone_row.addWidget(
            self.microphone_combo
        )

        voice_layout.addLayout(
            microphone_row
        )

        # ==========================================
        # WAKE SENSITIVITY
        # ==========================================

        wake_row = QHBoxLayout()

        self.wake_label = QLabel(
            "Wake-word sensitivity"
        )

        self.wake_label.setProperty(
            "class",
            "settingLabel",
        )

        self.wake_slider = QSlider(
            Qt.Orientation.Horizontal
        )

        self.wake_slider.setRange(
            10,
            100,
        )

        self.wake_slider.setMinimumWidth(
            260
        )

        self.wake_value = QLabel(
            "50%"
        )

        self.wake_value.setProperty(
            "class",
            "valueLabel",
        )

        self.wake_value.setMinimumWidth(
            42
        )

        self.wake_value.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        wake_row.addWidget(
            self.wake_label
        )

        wake_row.addStretch()

        wake_row.addWidget(
            self.wake_slider,
            2,
        )

        wake_row.addWidget(
            self.wake_value
        )

        voice_layout.addLayout(
            wake_row
        )

        # ==========================================
        # VOICE MODE
        # ==========================================

        voice_mode_row = QHBoxLayout()

        self.voice_mode_label = QLabel(
            "Voice mode"
        )

        self.voice_mode_label.setProperty(
            "class",
            "settingLabel",
        )

        self.voice_mode_combo = QComboBox()

        self.voice_mode_combo.addItems(
            [
                "XTTS",
                "ElevenLabs",
                "Offline",
            ]
        )

        voice_mode_row.addWidget(
            self.voice_mode_label
        )

        voice_mode_row.addStretch()

        voice_mode_row.addWidget(
            self.voice_mode_combo
        )

        voice_layout.addLayout(
            voice_mode_row
        )

        # ==========================================
        # ELEVENLABS
        # ==========================================

        elevenlabs_row = QHBoxLayout()

        self.elevenlabs_label = QLabel(
            "ElevenLabs voice"
        )

        self.elevenlabs_label.setProperty(
            "class",
            "settingLabel",
        )

        self.elevenlabs_combo = QComboBox()

        self.elevenlabs_combo.addItem(
            "Not configured"
        )

        elevenlabs_row.addWidget(
            self.elevenlabs_label
        )

        elevenlabs_row.addStretch()

        elevenlabs_row.addWidget(
            self.elevenlabs_combo
        )

        voice_layout.addLayout(
            elevenlabs_row
        )

        self.layout_main.addWidget(
            self.voice_panel
        )

        # ==========================================
        # INTERFACE TITLE
        # ==========================================

        self.interface_title = QLabel(
            "INTERFACE"
        )

        self.interface_title.setProperty(
            "class",
            "sectionTitle",
        )

        self.layout_main.addSpacing(
            5
        )

        self.layout_main.addWidget(
            self.interface_title
        )

        # ==========================================
        # INTERFACE PANEL
        # ==========================================

        self.interface_panel = QFrame()

        self.interface_panel.setObjectName(
            "settingPanel"
        )

        interface_layout = QVBoxLayout(
            self.interface_panel
        )

        interface_layout.setContentsMargins(
            18,
            10,
            18,
            10,
        )

        interface_layout.setSpacing(
            6
        )

        # ==========================================
        # OVERLAY
        # ==========================================

        overlay_row = QHBoxLayout()

        self.overlay_checkbox = QCheckBox(
            "Enable overlay"
        )

        overlay_row.addWidget(
            self.overlay_checkbox
        )

        overlay_row.addStretch()

        interface_layout.addLayout(
            overlay_row
        )

        # ==========================================
        # THEME
        # ==========================================

        theme_row = QHBoxLayout()

        self.theme_label = QLabel(
            "Theme"
        )

        self.theme_label.setProperty(
            "class",
            "settingLabel",
        )

        self.theme_combo = QComboBox()

        self.theme_combo.addItems(
            [
                "Dark",
                "Light",
            ]
        )

        theme_row.addWidget(
            self.theme_label
        )

        theme_row.addStretch()

        theme_row.addWidget(
            self.theme_combo
        )

        interface_layout.addLayout(
            theme_row
        )

        # ==========================================
        # ORB SCALE
        # ==========================================

        orb_row = QHBoxLayout()

        self.orb_label = QLabel(
            "Orb scale"
        )

        self.orb_label.setProperty(
            "class",
            "settingLabel",
        )

        self.orb_slider = QSlider(
            Qt.Orientation.Horizontal
        )

        self.orb_slider.setRange(
            80,
            140,
        )

        self.orb_slider.setMinimumWidth(
            260
        )

        self.orb_value = QLabel(
            "100%"
        )

        self.orb_value.setProperty(
            "class",
            "valueLabel",
        )

        self.orb_value.setMinimumWidth(
            42
        )

        self.orb_value.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        orb_row.addWidget(
            self.orb_label
        )

        orb_row.addStretch()

        orb_row.addWidget(
            self.orb_slider,
            2,
        )

        orb_row.addWidget(
            self.orb_value
        )

        interface_layout.addLayout(
            orb_row
        )

        # ==========================================
        # OVERLAY SCALE
        # ==========================================

        overlay_scale_row = QHBoxLayout()

        self.overlay_scale_label = QLabel(
            "Overlay scale"
        )

        self.overlay_scale_label.setProperty(
            "class",
            "settingLabel",
        )

        self.overlay_slider = QSlider(
            Qt.Orientation.Horizontal
        )

        self.overlay_slider.setRange(
            80,
            140,
        )

        self.overlay_slider.setMinimumWidth(
            260
        )

        self.overlay_value = QLabel(
            "100%"
        )

        self.overlay_value.setProperty(
            "class",
            "valueLabel",
        )

        self.overlay_value.setMinimumWidth(
            42
        )

        self.overlay_value.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        overlay_scale_row.addWidget(
            self.overlay_scale_label
        )

        overlay_scale_row.addStretch()

        overlay_scale_row.addWidget(
            self.overlay_slider,
            2,
        )

        overlay_scale_row.addWidget(
            self.overlay_value
        )

        interface_layout.addLayout(
            overlay_scale_row
        )

        self.layout_main.addWidget(
            self.interface_panel
        )

        # ==========================================
        # BOTTOM
        # ==========================================

        self.layout_main.addStretch()

        button_row = QHBoxLayout()

        self.reset_button = QPushButton(
            "Reset to Defaults"
        )

        self.back_button = QPushButton(
            "Back"
        )

        self.back_button.setObjectName(
            "backButton"
        )

        button_row.addWidget(
            self.reset_button
        )

        button_row.addStretch()

        button_row.addWidget(
            self.back_button
        )

        self.layout_main.addLayout(
            button_row
        )

        # ==========================================
        # SIGNALS
        # ==========================================

        self.back_button.clicked.connect(
            self.back_requested.emit
        )

        self.reset_button.clicked.connect(
            self.reset_settings
        )

        self.wake_slider.valueChanged.connect(
            self.handle_wake_changed
        )

        self.orb_slider.valueChanged.connect(
            self.handle_orb_changed
        )

        self.overlay_slider.valueChanged.connect(
            self.handle_overlay_scale_changed
        )

        self.voice_mode_combo.currentTextChanged.connect(
            self.handle_voice_mode_changed
        )

        self.overlay_checkbox.stateChanged.connect(
            self.handle_overlay_changed
        )

        self.theme_combo.currentTextChanged.connect(
            self.handle_theme_changed
        )

        self.apply_theme(
            self.current_theme
        )

    # ==================================================
    # THEME
    # ==================================================

    def apply_theme(
        self,
        theme,
    ):

        self.current_theme = theme.lower()

        if self.current_theme == "light":

            self.setStyleSheet(
                """
                QWidget#settingsScreen {
                    background: transparent;
                    color: #08202C;
                }

                QLabel {
                    background: transparent;
                    color: #08202C;
                }

                QLabel#settingsTitle {
                    color: #08202C;
                    font-size: 25px;
                    font-weight: 700;
                    letter-spacing: 6px;
                }

                QLabel.sectionTitle {
                    color: #008FB8;
                    font-size: 11px;
                    font-weight: 700;
                    letter-spacing: 2px;
                }

                QLabel.settingLabel {
                    color: #08202C;
                    font-size: 11px;
                }

                QLabel.valueLabel {
                    color: #26728A;
                    font-size: 10px;
                }

                QFrame#settingPanel {
                    background: rgba(225, 245, 250, 220);
                    border: 1px solid rgba(0, 130, 165, 100);
                    border-radius: 8px;
                }

                QFrame#separator {
                    background: rgba(0, 130, 165, 80);
                    border: none;
                    max-height: 1px;
                }

                QComboBox {
                    background: #F4FCFF;
                    color: #08202C;
                    border: 1px solid #69B5C9;
                    border-radius: 5px;
                    padding: 7px 10px;
                    min-width: 150px;
                    min-height: 26px;
                }

                QComboBox:hover {
                    border: 1px solid #00A8D6;
                }

                QComboBox QAbstractItemView {
                    background: #F4FCFF;
                    color: #08202C;
                    border: 1px solid #69B5C9;
                    selection-background-color: #B9EAF5;
                    selection-color: #06202D;
                }

                QSlider::groove:horizontal {
                    height: 3px;
                    background: #A9D2DC;
                }

                QSlider::sub-page:horizontal {
                    background: #00A8D6;
                }

                QSlider::add-page:horizontal {
                    background: #A9D2DC;
                }

                QSlider::handle:horizontal {
                    width: 12px;
                    height: 12px;
                    margin: -5px 0;
                    border-radius: 6px;
                    background: #00A8D6;
                }

                QCheckBox {
                    color: #08202C;
                }

                QPushButton {
                    background: #F4FCFF;
                    color: #08718D;
                    border: 1px solid #69B5C9;
                    border-radius: 5px;
                    padding: 8px 18px;
                }

                QPushButton:hover {
                    background: #DDF7FC;
                    border: 1px solid #00A8D6;
                    color: #00627D;
                }

                QPushButton#backButton {
                    background: #00A8D6;
                    color: #FFFFFF;
                    border: 1px solid #00CFFF;
                    font-weight: 700;
                }
                """
            )

        else:

            self.setStyleSheet(
                """
                QWidget#settingsScreen {
                    background: transparent;
                    color: #DDEFFF;
                }

                QLabel {
                    background: transparent;
                    color: #DDEFFF;
                }

                QLabel#settingsTitle {
                    color: #DDEFFF;
                    font-size: 25px;
                    font-weight: 700;
                    letter-spacing: 6px;
                }

                QLabel.sectionTitle {
                    color: #00D9FF;
                    font-size: 11px;
                    font-weight: 700;
                    letter-spacing: 2px;
                }

                QLabel.settingLabel {
                    color: #DDEFFF;
                    font-size: 11px;
                }

                QLabel.valueLabel {
                    color: #5C91B5;
                    font-size: 10px;
                }

                QFrame#settingPanel {
                    background: rgba(2, 14, 24, 190);
                    border: 1px solid rgba(0, 150, 210, 65);
                    border-radius: 8px;
                }

                QFrame#separator {
                    background: rgba(0, 150, 210, 50);
                    border: none;
                    max-height: 1px;
                }

                QComboBox {
                    background: #06131D;
                    color: #DDEFFF;
                    border: 1px solid #16445A;
                    border-radius: 5px;
                    padding: 7px 10px;
                    min-width: 150px;
                    min-height: 26px;
                }

                QComboBox:hover {
                    border: 1px solid #00D9FF;
                }

                QComboBox QAbstractItemView {
                    background: #06131D;
                    color: #DDEFFF;
                    border: 1px solid #16445A;
                    selection-background-color: #083C52;
                    selection-color: #00D9FF;
                }

                QSlider::groove:horizontal {
                    height: 3px;
                    background: #163746;
                }

                QSlider::sub-page:horizontal {
                    background: #00BFEF;
                }

                QSlider::add-page:horizontal {
                    background: #163746;
                }

                QSlider::handle:horizontal {
                    width: 12px;
                    height: 12px;
                    margin: -5px 0;
                    border-radius: 6px;
                    background: #00D9FF;
                }

                QCheckBox {
                    color: #DDEFFF;
                }

                QPushButton {
                    background: #06131D;
                    color: #8EDBF0;
                    border: 1px solid #16445A;
                    border-radius: 5px;
                    padding: 8px 18px;
                }

                QPushButton:hover {
                    background: #082331;
                    border: 1px solid #00D9FF;
                    color: #00D9FF;
                }

                QPushButton#backButton {
                    background: #00A8D6;
                    color: #001018;
                    border: 1px solid #00D9FF;
                    font-weight: 700;
                }
                """
            )

    # ==================================================
    # LOAD SETTINGS
    # ==================================================

    def load_settings(self):

        self._loading = True

        wake_value = int(
            self.settings_manager.wake_sensitivity * 100
        )

        self.wake_slider.setValue(
            wake_value
        )

        self.wake_value.setText(
            f"{wake_value}%"
        )

        voice_mode = (
            self.settings_manager.voice_mode
        )

        voice_index = (
            self.voice_mode_combo.findText(
                voice_mode
            )
        )

        if voice_index >= 0:

            self.voice_mode_combo.setCurrentIndex(
                voice_index
            )

        self.overlay_checkbox.setChecked(
            self.settings_manager.overlay_enabled
        )

        theme = (
            self.settings_manager.theme
        )

        theme_index = (
            self.theme_combo.findText(
                theme.capitalize()
            )
        )

        if theme_index >= 0:

            self.theme_combo.setCurrentIndex(
                theme_index
            )

        self.current_theme = theme.lower()

        orb_value = int(
            self.settings_manager.orb_scale * 100
        )

        self.orb_slider.setValue(
            orb_value
        )

        self.orb_value.setText(
            f"{orb_value}%"
        )

        overlay_value = int(
            self.settings_manager.overlay_scale * 100
        )

        self.overlay_slider.setValue(
            overlay_value
        )

        self.overlay_value.setText(
            f"{overlay_value}%"
        )

        self._loading = False

        self.apply_theme(
            self.current_theme
        )

    # ==================================================
    # HANDLERS
    # ==================================================

    def handle_wake_changed(
        self,
        value,
    ):

        self.wake_value.setText(
            f"{value}%"
        )

        if not self._loading:

            self.settings_manager.wake_sensitivity = (
                value / 100
            )

    def handle_orb_changed(
        self,
        value,
    ):

        self.orb_value.setText(
            f"{value}%"
        )

        if not self._loading:

            self.settings_manager.orb_scale = (
                value / 100
            )

    def handle_overlay_scale_changed(
        self,
        value,
    ):

        self.overlay_value.setText(
            f"{value}%"
        )

        if not self._loading:

            self.settings_manager.overlay_scale = (
                value / 100
            )

    def handle_voice_mode_changed(
        self,
        value,
    ):

        if not self._loading:

            self.settings_manager.voice_mode = (
                value
            )

    def handle_overlay_changed(
        self,
        state,
    ):

        if not self._loading:

            self.settings_manager.overlay_enabled = (
                state == Qt.CheckState.Checked.value
            )

    def handle_theme_changed(
        self,
        value,
    ):

        if self._loading:

            return

        theme = value.lower()

        self.settings_manager.theme = theme

        self.apply_theme(
            theme
        )

        self.theme_changed.emit(
            theme
        )

    # ==================================================
    # RESET
    # ==================================================

    def reset_settings(self):

        self.settings_manager.reset()

        self.load_settings()

        self.theme_changed.emit(
            self.settings_manager.theme
        )