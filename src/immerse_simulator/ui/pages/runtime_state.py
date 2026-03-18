from __future__ import annotations

from PySide6.QtWidgets import QLineEdit, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget


class RuntimeStatePage(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self.window = window
        layout = QVBoxLayout(self)
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Search state, puzzles, timers, conditions...")
        self.filter_edit.textChanged.connect(self.refresh)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Key", "Value", "Category", "Updated"])
        layout.addWidget(self.filter_edit)
        layout.addWidget(self.table)

    def refresh(self) -> None:
        snapshot = self.window.engine.state_manager.snapshot()
        filter_text = self.filter_edit.text().lower()
        rows = []
        for key, data in snapshot.items():
            if filter_text and filter_text not in key.lower() and filter_text not in str(data["value"]).lower():
                continue
            rows.append((key, str(data["value"]), str(data["category"]), str(data["updated_at"])))
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(value))
