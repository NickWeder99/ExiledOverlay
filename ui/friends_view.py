from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QListWidget, QListWidgetItem, QTextEdit
)
from PyQt6.QtCore import Qt
import json
import os

class FriendsView(QWidget):
    def __init__(self):
        super().__init__()
        self.friends_file = "friends.json"
        self.friends = self.load_friends()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Friends")
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: white;")
        layout.addWidget(title)
        
        # Add friend section
        add_layout = QHBoxLayout()
        self.friend_input = QLineEdit()
        self.friend_input.setPlaceholderText("Friend's account name...")
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_friend)
        
        add_layout.addWidget(self.friend_input)
        add_layout.addWidget(add_btn)
        layout.addLayout(add_layout)
        
        # Friends list
        self.friends_list = QListWidget()
        self.friends_list.itemClicked.connect(self.show_friend_info)
        layout.addWidget(self.friends_list)
        
        # Friend info display
        self.friend_info = QTextEdit()
        self.friend_info.setReadOnly(True)
        self.friend_info.setMaximumHeight(150)
        layout.addWidget(self.friend_info)
        
        self.setLayout(layout)
        self.refresh_list()

    def load_friends(self):
        if os.path.exists(self.friends_file):
            try:
                with open(self.friends_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_friends(self):
        try:
            with open(self.friends_file, 'w') as f:
                json.dump(self.friends, f, indent=2)
        except:
            pass

    def add_friend(self):
        friend_name = self.friend_input.text().strip()
        if friend_name and friend_name not in [f["name"] for f in self.friends]:
            self.friends.append({
                "name": friend_name,
                "status": "Unknown",
                "last_seen": "Never"
            })
            self.save_friends()
            self.refresh_list()
            self.friend_input.clear()

    def show_friend_info(self, item):
        row = self.friends_list.row(item)
        if 0 <= row < len(self.friends):
            friend = self.friends[row]
            info = f"Name: {friend['name']}\n"
            info += f"Status: {friend['status']}\n"
            info += f"Last Seen: {friend['last_seen']}\n"
            info += "Note: Gear viewing requires API access"
            self.friend_info.setText(info)

    def refresh_list(self):
        self.friends_list.clear()
        for friend in self.friends:
            list_item = QListWidgetItem(f"{friend['name']} ({friend['status']})")
            list_item.setForeground(Qt.GlobalColor.white)
            self.friends_list.addItem(list_item)