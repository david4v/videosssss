from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .app import MainWindow, configure_app


def main() -> None:
    app = QApplication(sys.argv)
    configure_app(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
