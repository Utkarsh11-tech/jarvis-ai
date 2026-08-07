from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window Properties
        self.setWindowTitle("JARVIS")
        self.resize(1000, 650)

        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main Layout
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # Title
        self.title = QLabel("JARVIS AI")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.main_layout.addWidget(self.title)