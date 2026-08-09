from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class ChromeProfileSelector(QDialog):

    profile_selected = Signal(str)

    def __init__(self, profiles, parent=None):
        super().__init__(parent)

        self.profiles = profiles

        self.setWindowTitle(
            "Select Chrome Profile"
        )

        self.setModal(True)

        self.resize(400, 300)

        # ==========================================
        # MAIN LAYOUT
        # ==========================================

        self.main_layout = QVBoxLayout()

        self.setLayout(
            self.main_layout
        )

        # ==========================================
        # TITLE
        # ==========================================

        self.title = QLabel(
            "Choose a Chrome profile"
        )

        self.main_layout.addWidget(
            self.title
        )

        # ==========================================
        # PROFILE BUTTONS
        # ==========================================

        for profile_directory, profile_data in profiles:

            profile_name = profile_data.get(
                "name",
                "Unknown"
            )

            button = QPushButton(
                profile_name
            )

            button.clicked.connect(
                lambda checked=False,
                directory=profile_directory:
                self.select_profile(directory)
            )

            self.main_layout.addWidget(
                button
            )

    def select_profile(self, profile_directory):
        """
        Sends the selected Chrome profile
        back to the application.
        """

        self.profile_selected.emit(
            profile_directory
        )

        self.accept()