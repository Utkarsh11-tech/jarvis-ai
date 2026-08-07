import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QVBoxLayout,
)

from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("JARVIS")
        self.resize(1000, 650)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()

        self.central_widget.setLayout(self.main_layout)

        title = QLabel("JARVIS AI")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.main_layout.addWidget(title)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())