# ui/gear_view.py
from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout, QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import requests
from api.poe_api import fetch_gear

def build_item_tooltip(item):
    rarity_colors = {
        0: "#BFBFBF", 1: "#8888FF", 2: "#FFFF77", 3: "#AF6025"
    }
    rarity = item.get("rarity", 0)
    color = rarity_colors.get(rarity, "#FFFFFF")
    name = item.get("name", "")
    type_line = item.get("type", "Unknown")
    tooltip = f"<b style='color:{color}'>{name or type_line}</b><br>"
    if name:
        tooltip += f"<i style='color:{color}'>{type_line}</i><br><br>"
    for mod in item.get("implicitMods", []):
        tooltip += f"<span style='color:#A2915D'>{mod}</span><br>"
    if item.get("explicitMods"):
        if item.get("implicitMods"): tooltip += "<br>"
        for mod in item["explicitMods"]:
            tooltip += f"<span style='color:#CCCCCC'>{mod}</span><br>"
    return tooltip

class GearView(QWidget):
    def __init__(self, gear_data):
        super().__init__()
        self.gear_data = gear_data
        self._build_ui()

    def _build_ui(self):
        slot_map = {
            "Weapon": (2, 0), "Helm": (0, 1), "Amulet": (1, 1), "Offhand": (2, 2),
            "Ring": (1, 0), "BodyArmour": (2, 1), "Ring2": (1, 2),
            "Gloves": (3, 0), "Belt": (3, 1), "Boots": (3, 2)
        }
        flask_slots = [f"Flask{i}" for i in range(1, 6)]

        gear_grid = QGridLayout()
        gear_grid.setContentsMargins(40, 40, 40, 80)
        gear_grid.setSpacing(10)

        for slot, (row, col) in slot_map.items():
            item = self.gear_data.get(slot)
            label = QLabel()
            if item and item.get("icon"):
                try:
                    img_data = requests.get(item["icon"]).content
                    pixmap = QPixmap()
                    pixmap.loadFromData(img_data)
                    label.setPixmap(pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio))
                    label.setToolTip(build_item_tooltip(item))
                except:
                    label.setText(item["type"])
            else:
                label.setText("Empty")
                label.setStyleSheet("color: gray;")
            gear_grid.addWidget(label, row, col)

        flask_layout = QHBoxLayout()
        for slot in flask_slots:
            item = self.gear_data.get(slot)
            label = QLabel()
            if item and item.get("icon"):
                try:
                    img_data = requests.get(item["icon"]).content
                    pixmap = QPixmap()
                    pixmap.loadFromData(img_data)
                    label.setPixmap(pixmap.scaled(40, 60, Qt.AspectRatioMode.KeepAspectRatio))
                    label.setToolTip(build_item_tooltip(item))
                except:
                    label.setText(item.get("type", "Unknown"))
            else:
                label.setText("Empty")
                label.setStyleSheet("color: gray;")
            flask_layout.addWidget(label)

        main_layout = QVBoxLayout()
        main_layout.addLayout(gear_grid)
        main_layout.addStretch()
        main_layout.addLayout(flask_layout)

        self.setLayout(main_layout)
