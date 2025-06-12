import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.overlay_window import OverlayWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_Use96Dpi)
    
    window = OverlayWindow()
    window.show()
    
    sys.exit(app.exec())