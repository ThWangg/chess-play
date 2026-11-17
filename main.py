"""
Entry point của ứng dụng Chess Desktop (Python + PySide6).
Chạy: py -3 main.py
"""
import sys

from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Chess - VKU DACS4")
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

