from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QLineEdit,
)
from PyQt6.QtCore import Qt
from api import poe_auth

class AccountView(QWidget):
    """Simple view for managing PoE account authorization."""

    def __init__(self) -> None:
        super().__init__()
        self._build_ui()
        self.update_status()

    def _build_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel("Account")
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: white;")
        layout.addWidget(title)

        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: white;")
        layout.addWidget(self.status_label)

        self.account_input = QLineEdit()
        self.account_input.setPlaceholderText("Account name (public client)")
        layout.addWidget(self.account_input)

        self.login_btn = QPushButton()
        self.login_btn.clicked.connect(self._login)
        layout.addWidget(self.login_btn)

        layout.addStretch()
        self.setLayout(layout)

    def update_status(self) -> None:
        token = poe_auth.load_token()
        if token:
            self.status_label.setText("Logged in")
            self.login_btn.setText("Re-authorize")
        else:
            self.status_label.setText("Not logged in")
            self.login_btn.setText("Log In")

    def _login(self) -> None:
        try:
            QMessageBox.information(
                self, "Login", "A browser window will open for login.")
            account = self.account_input.text().strip()
            if account:
                poe_auth.login_public(account)
            else:
                poe_auth.login()
            QMessageBox.information(
                self, "Login", "Authorization successful.")
        except Exception as exc:  # pragma: no cover - integration path
            QMessageBox.critical(self, "Login Failed", str(exc))
        self.update_status()
