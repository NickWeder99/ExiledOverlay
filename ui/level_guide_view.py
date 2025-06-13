from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QScrollArea, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor
from ui.modules.levelguide import LevelGuide

class LevelGuideView(QWidget):
    def __init__(self):
        super().__init__()
        self.level_guide = LevelGuide()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        title = QLabel("Leveling Guide")
        title.setStyleSheet("""
            font-weight: bold;
            font-size: 18px;
            font-family: 'Trade Gothic', 'Segoe UI', Arial, sans-serif;
        """)
        layout.addWidget(title)

        self.act_dropdown = QComboBox()
        self.act_dropdown.addItems(self.level_guide.get_acts())
        self.act_dropdown.currentIndexChanged.connect(self._on_act_selected)
        layout.addWidget(self.act_dropdown)


        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        # Ensure enough width for comfortable reading
        scroll.setMinimumWidth(280)

        self.text_widget = QTextEdit()
        self.text_widget.setReadOnly(True)
        self.text_widget.setStyleSheet("""
            font-family: 'Trade Gothic', 'Segoe UI', Arial, sans-serif;
            font-size: 14px;
        """)
        scroll.setWidget(self.text_widget)

        layout.addWidget(scroll)
        self.setLayout(layout)

        self._on_act_selected(0)

    def _on_act_selected(self, index):
        act = self.act_dropdown.itemText(index)
        tasks = self.level_guide.get_tasks_for_act(act)

        self.text_widget.clear()

        if tasks:
            cursor = self.text_widget.textCursor()
            fmt = cursor.blockFormat()
            fmt.setBottomMargin(10)  # space below each paragraph (step)
            cursor.setBlockFormat(fmt)

            for item in tasks:
                cursor.insertText(f"• {item}")
                cursor.insertBlock()
                fmt.setBottomMargin(10)
                cursor.setBlockFormat(fmt)

            # Move cursor to start so text view shows from the top
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.text_widget.setTextCursor(cursor)
        else:
            self.text_widget.setText("No guide available for this act.")

        

