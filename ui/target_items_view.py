from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt
import json
import os

class TargetItemsView(QWidget):
    def __init__(self):
        super().__init__()
        self.items_file = "target_items.json"
        self.target_items = self.load_items()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Target Items")
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: white;")
        layout.addWidget(title)
        
        # Add item section
        add_layout = QHBoxLayout()
        self.item_input = QLineEdit()
        self.item_input.setPlaceholderText("Item name...")
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Location/Source...")
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_item)
        
        add_layout.addWidget(self.item_input)
        add_layout.addWidget(self.location_input)
        add_layout.addWidget(add_btn)
        layout.addLayout(add_layout)
        
        # Items list
        self.items_list = QListWidget()
        self.items_list.itemDoubleClicked.connect(self.remove_item)
        layout.addWidget(self.items_list)
        
        # Info label
        info = QLabel("Double-click to remove items")
        info.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(info)
        
        self.setLayout(layout)
        self.refresh_list()

    def load_items(self):
        if os.path.exists(self.items_file):
            try:
                with open(self.items_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_items(self):
        try:
            with open(self.items_file, 'w') as f:
                json.dump(self.target_items, f, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save items: {e}")

    def add_item(self):
        item_name = self.item_input.text().strip()
        location = self.location_input.text().strip()
        
        if item_name and location:
            self.target_items.append({"name": item_name, "location": location})
            self.save_items()
            self.refresh_list()
            self.item_input.clear()
            self.location_input.clear()

    def remove_item(self, item):
        row = self.items_list.row(item)
        if 0 <= row < len(self.target_items):
            del self.target_items[row]
            self.save_items()
            self.refresh_list()

    def refresh_list(self):
        self.items_list.clear()
        for item in self.target_items:
            list_item = QListWidgetItem(f"{item['name']} - {item['location']}")
            list_item.setForeground(Qt.GlobalColor.white)
            self.items_list.addItem(list_item)
