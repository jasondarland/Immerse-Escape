from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QFileDialog


class EventLogPage(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self.window = window
        layout = QVBoxLayout(self)
        controls = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Filter logs")
        self.search.textChanged.connect(self.refresh)
        clear_button = QPushButton("Clear Visible Log")
        clear_button.clicked.connect(self._clear)
        export_button = QPushButton("Export Log")
        export_button.clicked.connect(self._export)
        controls.addWidget(self.search)
        controls.addWidget(clear_button)
        controls.addWidget(export_button)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Severity", "Source", "Room", "Type", "Message"])
        layout.addLayout(controls)
        layout.addWidget(self.table)

    def _clear(self) -> None:
        self.window.event_log.clear()
        self.refresh()

    def _export(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export Log", "event_log.csv", "CSV Files (*.csv)")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("timestamp,severity,source,room,type,message\n")
            for event in self.window.event_log:
                handle.write(f'"{event.timestamp}","{event.severity}","{event.source}","{event.room}","{event.event_type}","{event.message}"\n')

    def refresh(self) -> None:
        query = self.search.text().lower()
        filtered = [event for event in self.window.event_log if not query or query in event.message.lower() or query in event.source.lower()]
        self.table.setRowCount(len(filtered))
        for row, event in enumerate(filtered):
            values = [str(event.timestamp), event.severity, event.source, event.room, event.event_type, event.message]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))
