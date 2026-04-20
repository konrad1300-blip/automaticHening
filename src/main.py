import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from src.gui.splash_screen import SplashScreen
from src.gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    splash = SplashScreen()
    splash.show()
    print("Splash screen shown")

    main_window = None
    
    def show_main():
        nonlocal main_window
        main_window = MainWindow()
        main_window.show()
        splash.finish(main_window)
        print("Main window shown")

    QTimer.singleShot(2000, show_main)
    
    result = app.exec()
    print(f"App exiting with code: {result}")
    return result


if __name__ == "__main__":
    main()