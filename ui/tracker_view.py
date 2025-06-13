from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt
from api import poe_auth, poe_api
import json
import os

class TrackerView(QWidget):
    def __init__(self):
        super().__init__()
        self.trackers_file = "trackers.json"
        self.trackers = self.load_trackers()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Item Tracker")
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: white;")
        layout.addWidget(title)
        
        # Add tracker section
        add_layout = QVBoxLayout()
        
        item_layout = QHBoxLayout()
        item_layout.addWidget(QLabel("Item:"))
        self.item_input = QLineEdit()
        self.item_input.setPlaceholderText("Item to track...")
        item_layout.addWidget(self.item_input)
        add_layout.addLayout(item_layout)
        
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("Current Count:"))
        self.count_input = QSpinBox()
        self.count_input.setRange(0, 999999)
        count_layout.addWidget(self.count_input)
        add_layout.addLayout(count_layout)
        
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Target:"))
        self.target_input = QSpinBox()
        self.target_input.setRange(1, 999999)
        self.target_input.setValue(100)
        target_layout.addWidget(self.target_input)
        add_layout.addLayout(target_layout)
        
        add_btn = QPushButton("Add Tracker")
        add_btn.clicked.connect(self.add_tracker)
        add_layout.addWidget(add_btn)
        
        layout.addLayout(add_layout)
        
        # Trackers list
        self.trackers_list = QListWidget()
        self.trackers_list.itemDoubleClicked.connect(self.edit_tracker)
        layout.addWidget(self.trackers_list)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        increment_btn = QPushButton("+1")
        increment_btn.clicked.connect(lambda: self.modify_selected(1))
        btn_layout.addWidget(increment_btn)
        
        decrement_btn = QPushButton("-1")
        decrement_btn.clicked.connect(lambda: self.modify_selected(-1))
        btn_layout.addWidget(decrement_btn)
        
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_selected)
        btn_layout.addWidget(reset_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_selected)
        btn_layout.addWidget(remove_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.refresh_list()

    def load_trackers(self):
        if os.path.exists(self.trackers_file):
            try:
                with open(self.trackers_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_trackers(self):
        try:
            with open(self.trackers_file, 'w') as f:
                json.dump(self.trackers, f, indent=2)
        except:
            pass

    def add_tracker(self):
        item_name = self.item_input.text().strip()
        if item_name:
            count = self.count_input.value()
            try:
                token = poe_auth.ensure_valid_token("account:stashes")
                count = poe_api.fetch_item_count(
                    token.get("access_token"),
                    "Standard",
                    item_name,
                )
            except Exception:
                # Fall back to user provided value on error
                pass
            tracker = {
                "item": item_name,
                "current": count,
                "target": self.target_input.value(),
            }
            self.trackers.append(tracker)
            self.save_trackers()
            self.refresh_list()
            self.item_input.clear()
            self.count_input.setValue(0)
            self.target_input.setValue(100)

    def refresh_list(self):
        self.trackers_list.clear()
        for tracker in self.trackers:
            progress = (tracker["current"] / tracker["target"]) * 100
            text = f"{tracker['item']}: {tracker['current']}/{tracker['target']} ({progress:.1f}%)"
            
            list_item = QListWidgetItem(text)
            if tracker["current"] >= tracker["target"]:
                list_item.setForeground(Qt.GlobalColor.green)
            else:
                list_item.setForeground(Qt.GlobalColor.white)
            
            self.trackers_list.addItem(list_item)

    def modify_selected(self, change):
        current_row = self.trackers_list.currentRow()
        if 0 <= current_row < len(self.trackers):
            self.trackers[current_row]["current"] = max(0, self.trackers[current_row]["current"] + change)
            self.save_trackers()
            self.refresh_list()
            self.trackers_list.setCurrentRow(current_row)

    def reset_selected(self):
        current_row = self.trackers_list.currentRow()
        if 0 <= current_row < len(self.trackers):
            self.trackers[current_row]["current"] = 0
            self.save_trackers()
            self.refresh_list()
            self.trackers_list.setCurrentRow(current_row)

    def remove_selected(self):
        current_row = self.trackers_list.currentRow()
        if 0 <= current_row < len(self.trackers):
            del self.trackers[current_row]
            self.save_trackers()
            self.refresh_list()

    def edit_tracker(self, item):
        """Double-click to increment the selected tracker by 1."""
        self.modify_selected(1)
