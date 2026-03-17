"""Timeline editor page."""
from __future__ import annotations

import uuid
from PySide6.QtWidgets import QComboBox, QFormLayout, QHBoxLayout, QLineEdit, QListWidget, QPushButton, QSpinBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from escape_room_designer.models.project_model import TimelineCue


class TimelinePage(QWidget):
    def __init__(self):
        super().__init__()
        root = QHBoxLayout(self)
        left = QVBoxLayout(); right = QVBoxLayout()

        self.tracks = QListWidget(); self.tracks.addItems(["Lighting", "Audio", "Video", "Effects", "Doors / locks", "Puzzle events", "Operator actions", "Generic automation"])
        add_track = QPushButton("Add Track"); add_track.clicked.connect(lambda: self.tracks.addItem(f"Track {self.tracks.count()+1}"))
        del_track = QPushButton("Delete Track"); del_track.clicked.connect(lambda: self.tracks.takeItem(self.tracks.currentRow()))

        self.cues = QTableWidget(0, 7)
        self.cues.setHorizontalHeaderLabels(["ID", "Track", "Start(ms)", "Duration", "Mode", "Target", "Action"])

        left.addWidget(self.tracks); left.addWidget(add_track); left.addWidget(del_track); left.addWidget(self.cues,1)

        form = QFormLayout()
        self.name = QLineEdit("Cue")
        self.start = QSpinBox(); self.start.setMaximum(999999999)
        self.duration = QSpinBox(); self.duration.setMaximum(999999999)
        self.mode = QComboBox(); self.mode.addItems(["absolute_time", "relative_time", "conditional", "operator_manual", "logic_event"])
        self.target = QLineEdit()
        self.action = QLineEdit()
        add_cue = QPushButton("Add Cue"); add_cue.clicked.connect(self.add_cue)
        rem_cue = QPushButton("Remove Selected Cue"); rem_cue.clicked.connect(lambda: self.cues.removeRow(self.cues.currentRow()))

        form.addRow("Name", self.name); form.addRow("Start", self.start); form.addRow("Duration", self.duration)
        form.addRow("Trigger", self.mode); form.addRow("Target", self.target); form.addRow("Action", self.action)
        right.addLayout(form); right.addWidget(add_cue); right.addWidget(rem_cue); right.addStretch()

        root.addLayout(left,3); root.addLayout(right,1)

    def add_cue(self):
        row = self.cues.rowCount(); self.cues.insertRow(row)
        track = self.tracks.currentItem().text() if self.tracks.currentItem() else "Generic automation"
        vals = [f"cue-{uuid.uuid4().hex[:8]}", track, str(self.start.value()), str(self.duration.value()), self.mode.currentText(), self.target.text(), self.action.text() or self.name.text()]
        for c,v in enumerate(vals): self.cues.setItem(row,c,QTableWidgetItem(v))

    def export_timeline(self) -> list[TimelineCue]:
        out = []
        for r in range(self.cues.rowCount()):
            out.append(TimelineCue(id=self.cues.item(r,0).text(), track=self.cues.item(r,1).text(), start_time=int(self.cues.item(r,2).text()), duration=int(self.cues.item(r,3).text()), trigger_mode=self.cues.item(r,4).text(), target=self.cues.item(r,5).text(), action=self.cues.item(r,6).text()))
        return out

    def import_timeline(self, cues: list[TimelineCue]):
        self.cues.setRowCount(0)
        for c in cues:
            row=self.cues.rowCount(); self.cues.insertRow(row)
            vals=[c.id,c.track,str(c.start_time),str(c.duration),c.trigger_mode,c.target,c.action]
            for i,v in enumerate(vals): self.cues.setItem(row,i,QTableWidgetItem(v))
