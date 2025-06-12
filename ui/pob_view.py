from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox
)
import subprocess
import os

class PathOfBuildingView(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Path of Building")
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: white;")
        layout.addWidget(title)
        
        # Instructions
        info = QTextEdit()
        info.setReadOnly(True)
        info.setMaximumHeight(100)
        info.setText("""
Features:
• Export current gear to PoB
• Import passive tree
• Launch Path of Building

Note: Requires PoB installation and API access
        """)
        layout.addWidget(info)
        
        # Buttons
        export_btn = QPushButton("Export Gear to PoB")
        export_btn.clicked.connect(self.export_gear)
        layout.addWidget(export_btn)
        
        import_btn = QPushButton("Import from PoB")
        import_btn.clicked.connect(self.import_build)
        layout.addWidget(import_btn)
        
        launch_btn = QPushButton("Launch Path of Building")
        launch_btn.clicked.connect(self.launch_pob)
        layout.addWidget(launch_btn)
        
        layout.addStretch()
        self.setLayout(layout)

    def export_gear(self):
        QMessageBox.information(self, "Export", "Gear export functionality requires API implementation")

    def import_build(self):
        QMessageBox.information(self, "Import", "Import functionality requires PoB integration")

    def launch_pob(self):
        try:
            # Try common PoB installation paths
            pob_paths = [
                r"C:\ProgramData\Path of Building\Path of Building.exe",
                r"C:\Program Files\Path of Building\Path of Building.exe",
                r"C:\Program Files (x86)\Path of Building\Path of Building.exe"
            ]
            
            for path in pob_paths:
                if os.path.exists(path):
                    subprocess.Popen([path])
                    return
            
            QMessageBox.warning(self, "Error", "Path of Building not found in common installation directories")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch Path of Building: {e}")
