"""Simulation page."""
from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QListWidget, QPushButton, QVBoxLayout, QWidget


class SimulatorPage(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        grid = QGridLayout()
        self.log = QListWidget(); self.state_view = QListWidget()
        events = ["button_press", "keypad_entry", "rfid_scan", "door_open_close", "sensor_trigger", "relay_output", "puzzle_complete", "timer_expire", "media_finished"]
        for i,e in enumerate(events):
            b = QPushButton(e.replace('_',' ').title())
            b.clicked.connect(lambda _, x=e: self.simulate(x))
            grid.addWidget(b, i//3, i%3)
        root.addLayout(grid)
        root.addWidget(self.state_view)
        root.addWidget(self.log,1)

    def simulate(self, event):
        self.log.addItem(f"Simulated: {event}")
        self.log.addItem(f"Logic execution path: {event} -> evaluate -> dispatch")

    def bind_project(self, project):
        self.state_view.clear()
        self.state_view.addItems([f"{s.get('key')}: {s.get('default')}" for s in project.states] or ["No states"])
