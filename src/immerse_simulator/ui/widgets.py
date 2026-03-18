from __future__ import annotations

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout


class Card(QFrame):
    def __init__(self, title: str, value: str = "") -> None:
        super().__init__()
        self.setObjectName("metricCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)
        self.title_label = QLabel(title)
        self.title_label.setProperty("role", "secondary")
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("font-size: 20px; font-weight: 700;")
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)


class MetricsGrid(QFrame):
    def __init__(self, metrics: list[str]) -> None:
        super().__init__()
        self.setObjectName("pageFrame")
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setHorizontalSpacing(12)
        self.layout.setVerticalSpacing(12)
        self.cards = {}
        for index, name in enumerate(metrics):
            card = Card(name)
            self.cards[name] = card
            self.layout.addWidget(card, index // 3, index % 3)
