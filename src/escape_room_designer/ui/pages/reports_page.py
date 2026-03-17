"""Reports page with preview + filters."""
from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLineEdit, QListWidget, QPushButton, QTextEdit, QVBoxLayout, QWidget


class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        top = QHBoxLayout()
        self.report_type = QComboBox(); self.report_type.addItems(["Device list", "Puzzle list", "Room equipment list", "IO / patch list", "Reset checklist", "Operator checklist", "Media asset report", "Validation report", "Build/export manifest", "Bill of materials", "Maintenance notes"])
        self.room_filter = QLineEdit(); self.room_filter.setPlaceholderText("Filter room")
        self.type_filter = QLineEdit(); self.type_filter.setPlaceholderText("Filter device type")
        self.search = QLineEdit(); self.search.setPlaceholderText("Search")
        self.gen = QPushButton("Generate Preview")
        top.addWidget(self.report_type); top.addWidget(self.room_filter); top.addWidget(self.type_filter); top.addWidget(self.search); top.addWidget(self.gen)
        self.preview = QTextEdit(); self.preview.setReadOnly(True)
        self.list = QListWidget()
        root.addLayout(top); root.addWidget(self.preview,2); root.addWidget(self.list,1)
        self.gen.clicked.connect(self.generate)
        self._project = None

    def bind_project(self, project):
        self._project = project
        self.generate()

    def generate(self):
        if not self._project:
            return
        rt = self.report_type.currentText()
        text = [f"Report: {rt}", "="*40]
        if rt == "Device list":
            for d in self._project.devices: text.append(f"{d.id} | {d.name} | {d.type} | {d.room_id} | {d.address}")
        elif rt == "Puzzle list":
            for p in self._project.puzzle_nodes: text.append(f"{p.node_id} | {p.label}")
        elif rt == "Room equipment list":
            for r in self._project.layouts: text.append(f"{r.room_name}: {len(r.objects)} objects")
        elif rt == "Media asset report":
            for m in self._project.media: text.append(str(m))
        elif rt == "Build/export manifest":
            for e in self._project.recent_exports: text.append(str(e))
        else:
            text.append("Generated report for operational use.")
        self.preview.setPlainText("\n".join(text))
        self.list.clear(); self.list.addItems(text[2:] or ["No rows"])
