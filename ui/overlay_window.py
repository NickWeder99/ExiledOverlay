from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QFont

from ui.level_guide_view import LevelGuideView
from ui.target_items_view import TargetItemsView
from ui.friends_view import FriendsView
from ui.pob_view import PathOfBuildingView
from ui.currency_view import CurrencyView
from ui.tracker_view import TrackerView
from ui.account_view import AccountView

class OverlayWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PoE Overlay")
        
        # Position on left side of screen
        self.setGeometry(0, 100, 60, 600)
        self.setMinimumSize(60, 400)
        
        # Window flags for overlay
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        self._drag_active = False
        self._drag_start_pos = QPoint()
        
        self.is_expanded = False
        self.collapsed_width = 60
<<<<<<< w73mv5-codex/lokal-credentials-erstellen-und-speichern
        # Make the expanded overlay smaller so it overlaps the game less while
        # still leaving enough space for the main views.
        self.expanded_width = 420
=======
        # Allow a bit more room for the main view, especially the level guide
        # content which benefits from a wider display.
        self.expanded_width = 500
>>>>>>> main
        self.expanded_sidebar_width = 220
        
        self.modules = {
            "Account": AccountView(),
            "Levelguide": LevelGuideView(),
            "Target Items": TargetItemsView(),
            "Friends": FriendsView(),
            "Path of Building": PathOfBuildingView(),
            "Currency": CurrencyView(),
            "Tracker": TrackerView(),
        }
        
        self._init_ui()
        self._apply_styles()

    def _init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        main_widget.setLayout(self.main_layout)
        
        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(self.collapsed_width)
        self.sidebar.setFrameStyle(QFrame.Shape.StyledPanel)
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(5, 5, 5, 5)
        sidebar_layout.setSpacing(2)
        self.sidebar.setLayout(sidebar_layout)
        
        # Toggle button
        self.toggle_button = QPushButton("→")
        self.toggle_button.setFixedSize(50, 40)
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        sidebar_layout.addWidget(self.toggle_button)
        
        # Module buttons
        self.module_buttons = {}
        for name in self.modules.keys():
            btn = QPushButton(self._get_icon_for_module(name))
            btn.setFixedSize(50, 40)
            btn.setToolTip(name)
            btn.clicked.connect(lambda checked, n=name: self.switch_module(n))
            sidebar_layout.addWidget(btn)
            self.module_buttons[name] = btn
        
        sidebar_layout.addStretch()
        self.main_layout.addWidget(self.sidebar)
        
        # Content area (initially hidden)
        self.content_area = QStackedWidget()
        self.content_area.setVisible(False)
        for view in self.modules.values():
            self.content_area.addWidget(view)
        self.main_layout.addWidget(self.content_area)

    def _get_icon_for_module(self, module_name):
        icons = {
            "Account": "🔑",
            "Levelguide": "📖",
            "Target Items": "🎯",
            "Friends": "👥",
            "Path of Building": "🌳",
            "Currency": "💰",
            "Tracker": "📊"
        }
        return icons.get(module_name, "📋")

    def _apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: rgba(30, 30, 30, 200);
                border: 1px solid #555;
            }
            QFrame {
                background-color: rgba(40, 40, 40, 220);
                border: 1px solid #666;
            }
            QPushButton {
                background-color: rgba(60, 60, 60, 200);
                border: 1px solid #888;
                color: white;
                font-size: 14px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: rgba(80, 80, 80, 220);
            }
            QPushButton:pressed {
                background-color: rgba(100, 100, 100, 220);
            }
            QStackedWidget {
                background-color: rgba(35, 35, 35, 220);
                border: 1px solid #666;
            }
        """)

    def toggle_sidebar(self):
        self.is_expanded = not self.is_expanded
        
        if self.is_expanded:
            self.setFixedWidth(self.expanded_width)
            self.sidebar.setFixedWidth(self.expanded_sidebar_width)
            self.content_area.setVisible(True)
            self.toggle_button.setText("←")
            
            # Update button text
            for name, btn in self.module_buttons.items():
                btn.setText(f"{self._get_icon_for_module(name)} {name}")
                btn.setFixedSize(200, 40)
        else:
            self.setFixedWidth(self.collapsed_width)
            self.sidebar.setFixedWidth(self.collapsed_width)
            self.content_area.setVisible(False)
            self.toggle_button.setText("→")
            
            # Reset button text to icons only
            for name, btn in self.module_buttons.items():
                btn.setText(self._get_icon_for_module(name))
                btn.setFixedSize(50, 40)

    def switch_module(self, module_name):
        if not self.is_expanded:
            self.toggle_sidebar()
        
        index = list(self.modules.keys()).index(module_name)
        self.content_area.setCurrentIndex(index)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = True
            self._drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_active:
            self.move(event.globalPosition().toPoint() - self._drag_start_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_active = False
        event.accept()