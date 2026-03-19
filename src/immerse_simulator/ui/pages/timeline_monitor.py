from __future__ import annotations

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget


class TimelineMonitorPage(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self.window = window
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Track", "Cue", "Trigger Mode", "Start", "Duration", "Target", "State"])
        layout.addWidget(self.table)

    def refresh(self) -> None:
        package = self.window.engine.package
        cues = package.timeline if package else []
        self.table.setRowCount(len(cues))
        for row, cue in enumerate(cues):
            values = [cue.track, cue.name, cue.trigger_mode, cue.cue_id, str(cue.duration), f"{cue.target_device}:{cue.action}", cue.state]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))
