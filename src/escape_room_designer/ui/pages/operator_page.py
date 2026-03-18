"""Operator control page."""
from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QGridLayout, QLabel, QListWidget, QPushButton, QVBoxLayout, QWidget


class OperatorPage(QWidget):
    def __init__(self):
        super().__init__()
        self.elapsed = 0
        root = QVBoxLayout(self)
        grid = QGridLayout()
        self.buttons = {}
        controls = ["start_game", "pause_game", "resume_game", "stop_game", "reset_game", "skip_puzzle", "trigger_hint", "force_unlock_door", "emergency_unlock_all", "trigger_finale", "restart_media"]
        for i,c in enumerate(controls):
            b=QPushButton(c.replace('_',' ').title()); b.clicked.connect(lambda _,x=c:self.log_event(f"Operator action: {x}")); self.buttons[c]=b; grid.addWidget(b,i//3,i%3)
        root.addLayout(grid)
        self.timer_lbl = QLabel("Game Timer: 00:00")
        self.progress = QListWidget(); self.room_status = QListWidget(); self.door_status = QListWidget(); self.sensor_status = QListWidget(); self.media_status = QListWidget(); self.active_cues = QListWidget(); self.event_log = QListWidget(); self.alerts = QListWidget()
        for w,t in [(self.progress,"Puzzle progress"),(self.room_status,"Room status"),(self.door_status,"Door status"),(self.sensor_status,"Sensor status"),(self.media_status,"Media"),(self.active_cues,"Active cues"),(self.alerts,"Alerts")]: w.addItem(t)
        root.addWidget(self.timer_lbl); root.addWidget(self.event_log,1)
        self.clock=QTimer(self); self.clock.timeout.connect(self.tick); self.clock.start(1000)

    def tick(self):
        self.elapsed += 1
        m,s=divmod(self.elapsed,60)
        self.timer_lbl.setText(f"Game Timer: {m:02}:{s:02}")

    def log_event(self, text):
        self.event_log.addItem(text)

    def bind_project(self, project):
        self.progress.clear(); self.progress.addItems([n.label for n in project.puzzle_nodes] or ["No puzzles"])
        self.room_status.clear(); self.room_status.addItems([f"{r.room_name}: ready" for r in project.layouts])
        self.door_status.clear(); self.door_status.addItems([f"{d.name}: {d.default_state}" for d in project.devices if 'lock' in d.type or 'door' in d.type] or ["No door devices"])
        self.sensor_status.clear(); self.sensor_status.addItems([f"{d.name}: idle" for d in project.devices if 'sensor' in d.type] or ["No sensors"])
        self.media_status.clear(); self.media_status.addItems([m.get('asset_id',m.get('name','asset')) for m in project.media] or ["No media"])
        self.active_cues.clear(); self.active_cues.addItems([c.id for c in project.timeline] or ["No timeline cues"])
