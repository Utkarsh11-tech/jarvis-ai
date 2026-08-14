from PySide6.QtCore import QSettings


class SettingsManager:

    ORGANIZATION = "JARVIS"
    APPLICATION = "JARVIS"

    DEFAULTS = {
        "microphone": -1,
        "wake_sensitivity": 0.5,
        "voice_mode": "XTTS",
        "elevenlabs_voice": "",
        "overlay_enabled": True,
        "theme": "dark",
        "orb_scale": 1.0,
        "overlay_scale": 1.0,
    }

    def __init__(self):

        self.settings = QSettings(
            self.ORGANIZATION,
            self.APPLICATION,
        )

    # ==================================================
    # GET
    # ==================================================

    def get(
        self,
        key,
    ):

        default = self.DEFAULTS.get(
            key
        )

        return self.settings.value(
            key,
            default,
        )

    # ==================================================
    # SET
    # ==================================================

    def set(
        self,
        key,
        value,
    ):

        self.settings.setValue(
            key,
            value,
        )

        self.settings.sync()

    # ==================================================
    # RESET
    # ==================================================

    def reset(self):

        self.settings.clear()

        for key, value in self.DEFAULTS.items():

            self.settings.setValue(
                key,
                value,
            )

        self.settings.sync()

    # ==================================================
    # INDIVIDUAL SETTINGS
    # ==================================================

    @property
    def microphone(self):

        return int(
            self.get(
                "microphone"
            )
        )

    @microphone.setter
    def microphone(
        self,
        value,
    ):

        self.set(
            "microphone",
            int(value),
        )

    @property
    def wake_sensitivity(self):

        return float(
            self.get(
                "wake_sensitivity"
            )
        )

    @wake_sensitivity.setter
    def wake_sensitivity(
        self,
        value,
    ):

        self.set(
            "wake_sensitivity",
            float(value),
        )

    @property
    def voice_mode(self):

        return str(
            self.get(
                "voice_mode"
            )
        )

    @voice_mode.setter
    def voice_mode(
        self,
        value,
    ):

        self.set(
            "voice_mode",
            str(value),
        )

    @property
    def elevenlabs_voice(self):

        return str(
            self.get(
                "elevenlabs_voice"
            )
        )

    @elevenlabs_voice.setter
    def elevenlabs_voice(
        self,
        value,
    ):

        self.set(
            "elevenlabs_voice",
            str(value),
        )

    @property
    def overlay_enabled(self):

        value = self.get(
            "overlay_enabled"
        )

        if isinstance(value, str):

            return value.lower() in (
                "true",
                "1",
                "yes",
                "on",
            )

        return bool(value)

    @overlay_enabled.setter
    def overlay_enabled(
        self,
        value,
    ):

        self.set(
            "overlay_enabled",
            bool(value),
        )

    @property
    def theme(self):

        return str(
            self.get(
                "theme"
            )
        )

    @theme.setter
    def theme(
        self,
        value,
    ):

        self.set(
            "theme",
            str(value),
        )

    @property
    def orb_scale(self):

        return float(
            self.get(
                "orb_scale"
            )
        )

    @orb_scale.setter
    def orb_scale(
        self,
        value,
    ):

        self.set(
            "orb_scale",
            float(value),
        )

    @property
    def overlay_scale(self):

        return float(
            self.get(
                "overlay_scale"
            )
        )

    @overlay_scale.setter
    def overlay_scale(
        self,
        value,
    ):

        self.set(
            "overlay_scale",
            float(value),
        )