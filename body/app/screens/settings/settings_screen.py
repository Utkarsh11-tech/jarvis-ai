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

    theme_changed = Signal(str)

    def __init__(
        self,
        settings_manager,
        parent=None,
    ):
        super().__init__(parent)

        self.settings_manager = settings_manager

        self._loading = False

        self.current_theme = (
            self.settings_manager.theme
        )

        self.build_ui()

        self.load_settings()

    # ==================================================
    # BUILD UI
    # ==================================================

    def build_ui(self):

        self.setObjectName(
            "settingsScreen"
        )

        self.layout_main = QVBoxLayout(
            self
        )

        self.layout_main.setContentsMargins(
            30,
            20,
            30,
            20,
        )

        self.layout_main.setSpacing(
            10
        )

        # ==================================================
        # TITLE
        # ==================================================

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

        # ==================================================
        # VOICE SECTION
        # ==================================================

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

        self.voice_panel = QFrame()

        self.voice_panel.setObjectName(
            "settingPanel"
        )

        voice_layout = QVBoxLayout(
            self.voice_panel
        )

        voice_layout.setContentsMargins(
            16,
            8,
            16,
            8,
        )

        voice_layout.setSpacing(
            0
        )

        # --------------------------------------------------
        # MICROPHONE
        # --------------------------------------------------

        microphone_row = self.create_setting_row(
            "◉",
            "Microphone",
            "Select your input device",
        )

        self.microphone_combo = QComboBox()

        self.microphone_combo.addItem(
            "Default Microphone",
            -1,
        )

        microphone_row.addWidget(
            self.microphone_combo
        )

        voice_layout.addLayout(
            microphone_row
        )

        # --------------------------------------------------
        # WAKE SENSITIVITY
        # --------------------------------------------------

        wake_row = self.create_setting_row(
            "〽",
            "Wake-word sensitivity",
            "Adjust how sensitive J.A.R.V.I.S listens for the wake word",
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
            45
        )

        wake_row.addWidget(
            QLabel("−")
        )

        wake_row.addWidget(
            self.wake_slider,
            1,
        )

        wake_row.addWidget(
            QLabel("+")
        )

        wake_row.addWidget(
            self.wake_value
        )

        voice_layout.addLayout(
            wake_row
        )

        # --------------------------------------------------
        # VOICE MODE
        # --------------------------------------------------

        voice_mode_row = self.create_setting_row(
            "◖",
            "Voice mode",
            "Select the voice engine",
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
            self.voice_mode_combo
        )

        voice_layout.addLayout(
            voice_mode_row
        )

        # --------------------------------------------------
        # ELEVENLABS
        # --------------------------------------------------

        elevenlabs_row = self.create_setting_row(
            "♙",
            "ElevenLabs voice",
            "Select your ElevenLabs voice",
        )

        self.elevenlabs_combo = QComboBox()

        self.elevenlabs_combo.addItem(
            "Not configured"
        )

        elevenlabs_row.addWidget(
            self.elevenlabs_combo
        )

        voice_layout.addLayout(
            elevenlabs_row
        )

        self.layout_main.addWidget(
            self.voice_panel
        )

        # ==================================================
        # INTERFACE SECTION
        # ==================================================

        self.interface_title = QLabel(
            "INTERFACE"
        )

        self.interface_title.setProperty(
            "class",
            "sectionTitle",
        )

        self.layout_main.addWidget(
            self.interface_title
        )

        self.interface_panel = QFrame()

        self.interface_panel.setObjectName(
            "settingPanel"
        )

        interface_layout = QVBoxLayout(
            self.interface_panel
        )

        interface_layout.setContentsMargins(
            16,
            8,
            16,
            8,
        )

        interface_layout.setSpacing(
            0
        )

        # --------------------------------------------------
        # OVERLAY
        # --------------------------------------------------

        overlay_row = self.create_setting_row(
            "▣",
            "Enable overlay",
            "Show the wake word overlay when J.A.R.V.I.S detects you",
        )

        self.overlay_checkbox = QCheckBox()

        overlay_row.addWidget(
            self.overlay_checkbox
        )

        interface_layout.addLayout(
            overlay_row
        )

        # --------------------------------------------------
        # THEME
        # --------------------------------------------------

        theme_row = self.create_setting_row(
            "◌",
            "Theme",
            "Choose your preferred theme",
        )

        self.theme_combo = QComboBox()

        self.theme_combo.addItems(
            [
                "Dark",
                "Light",
            ]
        )

        theme_row.addWidget(
            self.theme_combo
        )

        interface_layout.addLayout(
            theme_row
        )

        # --------------------------------------------------
        # ORB SCALE
        # --------------------------------------------------

        orb_row = self.create_setting_row(
            "◉",
            "Orb scale",
            "Adjust the size of the central orb",
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

        orb_row.addWidget(
            QLabel("−")
        )

        orb_row.addWidget(
            self.orb_slider,
            1,
        )

        orb_row.addWidget(
            QLabel("+")
        )

        orb_row.addWidget(
            self.orb_value
        )

        interface_layout.addLayout(
            orb_row
        )

        # --------------------------------------------------
        # OVERLAY SCALE
        # --------------------------------------------------

        overlay_scale_row = self.create_setting_row(
            "□",
            "Overlay scale",
            "Adjust the size of the overlay",
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

        overlay_scale_row.addWidget(
            QLabel("−")
        )

        overlay_scale_row.addWidget(
            self.overlay_slider,
            1,
        )

        overlay_scale_row.addWidget(
            QLabel("+")
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

        # ==================================================
        # SPACER
        # ==================================================

        self.layout_main.addStretch()

        # ==================================================
        # RESET
        # ==================================================

        button_row = QHBoxLayout()

        button_row.addStretch()

        self.reset_button = QPushButton(
            "Reset to Defaults"
        )

        self.reset_button.setObjectName(
            "resetButton"
        )

        button_row.addWidget(
            self.reset_button
        )

        self.layout_main.addLayout(
            button_row
        )

        # ==================================================
        # SIGNALS
        # ==================================================

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

        self.microphone_combo.currentIndexChanged.connect(
            self.handle_microphone_changed
        )

        self.apply_theme(
            self.current_theme
        )

    # ==================================================
    # CREATE SETTING ROW
    # ==================================================

    def create_setting_row(
        self,
        icon,
        title,
        description,
    ):

        row = QHBoxLayout()

        row.setContentsMargins(
            8,
            10,
            8,
            10,
        )

        row.setSpacing(
            12
        )

        icon_label = QLabel(
            icon
        )

        icon_label.setProperty(
            "class",
            "settingIcon",
        )

        icon_label.setFixedWidth(
            30
        )

        title_label = QLabel(
            title
        )

        title_label.setProperty(
            "class",
            "settingTitle",
        )

        description_label = QLabel(
            description
        )

        description_label.setProperty(
            "class",
            "settingDescription",
        )

        text_layout = QVBoxLayout()

        text_layout.setSpacing(
            2
        )

        text_layout.addWidget(
            title_label
        )

        text_layout.addWidget(
            description_label
        )

        row.addWidget(
            icon_label
        )

        row.addLayout(
            text_layout,
            1,
        )

        return row

    # ==================================================
    # LOAD
    # ==================================================

    def load_settings(self):

        self._loading = True

        wake_value = int(
            self.settings_manager.wake_sensitivity
            * 100
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

        index = (
            self.voice_mode_combo.findText(
                voice_mode
            )
        )

        if index >= 0:

            self.voice_mode_combo.setCurrentIndex(
                index
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
            self.settings_manager.orb_scale
            * 100
        )

        self.orb_slider.setValue(
            orb_value
        )

        self.orb_value.setText(
            f"{orb_value}%"
        )

        overlay_value = int(
            self.settings_manager.overlay_scale
            * 100
        )

        self.overlay_slider.setValue(
            overlay_value
        )

        self.overlay_value.setText(
            f"{overlay_value}%"
        )

        microphone = (
            self.settings_manager.microphone
        )

        microphone_index = (
            self.microphone_combo.findData(
                microphone
            )
        )

        if microphone_index >= 0:

            self.microphone_combo.setCurrentIndex(
                microphone_index
            )

        self._loading = False

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

            background = "#EAF8FC"
            panel = "#F4FCFE"
            text = "#08202C"
            secondary = "#477B8C"
            cyan = "#008FB8"
            border = "#69B5C9"
            control = "#F8FEFF"

        else:

            background = "#020912"
            panel = "#06131D"
            text = "#DDEFFF"
            secondary = "#7B9DB0"
            cyan = "#00D9FF"
            border = "#16445A"
            control = "#06131D"

        self.setStyleSheet(
            f"""
            QWidget#settingsScreen {{
                background: transparent;
                color: {text};
            }}

            QLabel {{
                background: transparent;
                color: {text};
            }}

            QLabel#settingsTitle {{
                color: {text};
                font-family:
                    "Orbitron",
                    "Eurostile",
                    "Arial";
                font-size: 26px;
                font-weight: 700;
                letter-spacing: 7px;
            }}

            QLabel.sectionTitle {{
                color: {cyan};
                font-family:
                    "Orbitron",
                    "Eurostile",
                    "Arial";
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 3px;
                padding-top: 8px;
            }}

            QFrame#settingPanel {{
                background: {panel};
                border: 1px solid {border};
                border-radius: 12px;
            }}

            QLabel.settingIcon {{
                color: {cyan};
                font-size: 22px;
                font-weight: bold;
            }}

            QLabel.settingTitle {{
                color: {text};
                font-size: 13px;
                font-weight: 600;
            }}

            QLabel.settingDescription {{
                color: {secondary};
                font-size: 10px;
            }}

            QLabel.valueLabel {{
                color: {cyan};
                font-size: 11px;
                font-weight: 600;
            }}

            QComboBox {{
                background: {control};
                color: {text};
                border: 1px solid {border};
                border-radius: 7px;
                padding: 7px 12px;
                min-width: 170px;
                min-height: 28px;
            }}

            QComboBox:hover {{
                border: 1px solid {cyan};
            }}

            QComboBox QAbstractItemView {{
                background: {control};
                color: {text};
                border: 1px solid {border};
                selection-background-color: #083C52;
                selection-color: {cyan};
            }}

            QSlider::groove:horizontal {{
                height: 4px;
                background: {border};
                border-radius: 2px;
            }}

            QSlider::sub-page:horizontal {{
                background: {cyan};
                border-radius: 2px;
            }}

            QSlider::add-page:horizontal {{
                background: {border};
                border-radius: 2px;
            }}

            QSlider::handle:horizontal {{
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
                background: {cyan};
            }}

            QCheckBox {{
                background: {control};
                border: 1px solid {border};
                border-radius: 14px;
                padding: 4px;
                color: {cyan};
            }}

            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}

            QPushButton#resetButton {{
                background: transparent;
                color: {cyan};
                border: 1px solid {cyan};
                border-radius: 7px;
                padding: 9px 22px;
                font-weight: 600;
            }}

            QPushButton#resetButton:hover {{
                background: rgba(0, 217, 255, 25);
            }}
            """
        )

    # ==================================================
    # HANDLERS
    # ==================================================

    def handle_microphone_changed(
        self,
        index,
    ):

        if self._loading:
            return

        data = self.microphone_combo.itemData(
            index
        )

        if data is not None:

            self.settings_manager.microphone = (
                int(data)
            )

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

            self.settings_manager.voice_mode = value

    def handle_overlay_changed(
        self,
        state,
    ):

        if not self._loading:

            self.settings_manager.overlay_enabled = (
                state
                == Qt.CheckState.Checked.value
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

    def reset_settings(
        self,
    ):

        self.settings_manager.reset()

        self.load_settings()

        self.theme_changed.emit(
            self.settings_manager.theme
        )