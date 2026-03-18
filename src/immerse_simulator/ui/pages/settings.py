from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QComboBox, QFormLayout, QWidget


class SettingsPage(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self.window = window
        layout = QFormLayout(self)
        self.speed = QComboBox()
        self.speed.addItems(["0.5x", "1x", "2x", "5x"])
        self.speed.setCurrentText("1x")
        self.speed.currentTextChanged.connect(self._speed_changed)
        self.dark_theme = QCheckBox()
        self.dark_theme.setChecked(True)
        self.auto_load = QCheckBox()
        self.auto_load.setChecked(True)
        self.auto_start = QCheckBox()
        self.demo_mode = QCheckBox()
        self.demo_mode.setChecked(True)
        self.media_mode = QComboBox()
        self.media_mode.addItems(["Simulated", "Placeholder Playback"])
        self.verbosity = QComboBox()
        self.verbosity.addItems(["Info", "Debug", "Verbose"])
        self.startup_room = QComboBox()
        self.startup_room.addItems(["Lab A", "Lab B"])
        layout.addRow("Simulation Speed", self.speed)
        layout.addRow("Dark Theme", self.dark_theme)
        layout.addRow("Auto-load Last Package", self.auto_load)
        layout.addRow("Auto-start Session", self.auto_start)
        layout.addRow("Demo Mode", self.demo_mode)
        layout.addRow("Media Simulation Mode", self.media_mode)
        layout.addRow("Log Verbosity", self.verbosity)
        layout.addRow("Startup Room", self.startup_room)

    def _speed_changed(self, text: str) -> None:
        self.window.engine.session.speed = float(text.replace('x', ''))
        self.window.refresh_all()

    def refresh(self) -> None:
        return
