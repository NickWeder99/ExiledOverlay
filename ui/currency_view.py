from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QPushButton
)
from PyQt6.QtCore import Qt, QTimer
import json
import os
from api import poe_api, poe_auth

class CurrencyView(QWidget):
    def __init__(self):
        super().__init__()
        self.currency_file = "currency.json"
        self.currency_data = self.load_currency()
        self._build_ui()
        
        # Auto-refresh timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_currency)
        self.timer.start(30000)  # Refresh every 30 seconds

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Currency")
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: white;")
        layout.addWidget(title)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_currency)
        layout.addWidget(refresh_btn)
        
        # Currency grid
        self.currency_grid = QGridLayout()
        layout.addLayout(self.currency_grid)
        
        layout.addStretch()
        self.setLayout(layout)
        self.update_display()

    def load_currency(self):
        # Default currency types
        default_currency = {
            "Chaos Orb": 0,
            "Divine Orb": 0,
            "Exalted Orb": 0,
            "Mirror of Kalandra": 0,
            "Ancient Orb": 0,
            "Chromatic Orb": 0,
            "Jeweller's Orb": 0,
            "Orb of Fusing": 0
        }
        
        if os.path.exists(self.currency_file):
            try:
                with open(self.currency_file, 'r') as f:
                    loaded = json.load(f)
                    default_currency.update(loaded)
            except:
                pass
        
        return default_currency

    def save_currency(self):
        try:
            with open(self.currency_file, 'w') as f:
                json.dump(self.currency_data, f, indent=2)
        except:
            pass

    def update_display(self):
        # Clear existing widgets
        for i in reversed(range(self.currency_grid.count())):
            self.currency_grid.itemAt(i).widget().setParent(None)
        
        row = 0
        for currency, amount in self.currency_data.items():
            # Currency name
            name_label = QLabel(currency)
            name_label.setStyleSheet("color: white; font-weight: bold;")
            self.currency_grid.addWidget(name_label, row, 0)
            
            # Amount
            amount_label = QLabel(str(amount))
            amount_label.setStyleSheet("color: #ffff77; font-size: 14px;")
            amount_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            self.currency_grid.addWidget(amount_label, row, 1)
            
            row += 1

    def refresh_currency(self):
        """Update currency counts using the PoE API."""
        try:
            token = poe_auth.ensure_valid_token("account:stashes")
            counts = poe_api.fetch_currency(
                token.get("access_token"),
                "Standard",
                list(self.currency_data.keys()),
            )
            self.currency_data.update(counts)
            self.save_currency()
        except Exception:
            # Fall back to stored data if anything goes wrong
            self.currency_data = self.load_currency()
        self.update_display()
