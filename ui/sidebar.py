# ui/sidebar.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal

class Sidebar(QWidget):
    module_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.expanded = False
        self.setFixedWidth(40)
        self._build_ui()

    def _build_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.toggle_btn = QPushButton("▶")
        self.toggle_btn.clicked.connect(self.toggle)
        self.layout.addWidget(self.toggle_btn)

        self.buttons = {}
        for name in ["Levelguide", "Target Items", "Friends", "Path of Building", "Currency", "Tracker"]:
            btn = QPushButton(name)
            btn.setVisible(False)
            btn.clicked.connect(lambda _, n=name: self.module_selected.emit(n))
            self.layout.addWidget(btn)
            self.buttons[name] = btn

        self.layout.addStretch()

    def toggle(self):
        self.expanded = not self.expanded
        self.setFixedWidth(200 if self.expanded else 40)
        for btn in self.buttons.values():
            btn.setVisible(self.expanded)
        self.toggle_btn.setText("◀" if self.expanded else "▶")
