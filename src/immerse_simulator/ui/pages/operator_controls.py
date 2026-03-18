from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class OperatorControlsPage(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self.window = window
        layout = QVBoxLayout(self)
        self.room_selector = QComboBox()
        self.room_selector.currentTextChanged.connect(self._room_changed)
        self.summary = QLabel("Embedded OCC controls")
        grid = QGridLayout()
        actions = [
            "Start Game", "Pause", "Resume", "Stop", "Reset Room", "Full Reset", "Skip Puzzle",
            "Trigger Hint", "Trigger Hint 2", "Trigger Finale", "Emergency Unlock All",
            "Stop All Audio", "Stop All Video", "Blackout / Kill FX", "Restore Defaults",
        ]
        for idx, action in enumerate(actions):
            button = QPushButton(action)
            button.clicked.connect(lambda checked=False, value=action: self.window.engine.trigger_operator_action(value))
            grid.addWidget(button, idx // 3, idx % 3)
        layout.addWidget(self.room_selector)
        layout.addWidget(self.summary)
        layout.addLayout(grid)

    def _room_changed(self, room: str) -> None:
        if room:
            self.window.engine.active_room = room
            self.window.refresh_all()

    def refresh(self) -> None:
        package = self.window.engine.package
        self.room_selector.blockSignals(True)
        current = self.room_selector.currentText()
        self.room_selector.clear()
        if package:
            rooms = [room.get("name", "Unnamed Room") for room in package.rooms]
            self.room_selector.addItems(rooms)
            if self.window.engine.active_room in rooms:
                self.room_selector.setCurrentText(self.window.engine.active_room)
            elif current in rooms:
                self.room_selector.setCurrentText(current)
        self.room_selector.blockSignals(False)
        audio = self.window.engine.media.audio_state
        video = self.window.engine.media.video_state
        self.summary.setText(f"Alerts: {', '.join(self.window.engine.active_alerts) or 'None'} | Audio: {audio['status']} | Video: {video['status']}")
