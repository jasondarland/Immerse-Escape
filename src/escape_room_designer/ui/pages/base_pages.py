"""Reusable page widgets."""
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class PlaceholderPage(QWidget):
    def __init__(self, title: str, description: str):
        super().__init__()
        layout = QVBoxLayout(self)
        heading = QLabel(f"<h2>{title}</h2>")
        body = QLabel(description)
        body.setWordWrap(True)
        layout.addWidget(heading)
        layout.addWidget(body)
        layout.addStretch()
