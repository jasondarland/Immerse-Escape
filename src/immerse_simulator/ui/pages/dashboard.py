from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QPushButton, QVBoxLayout, QWidget

from immerse_simulator.ui.widgets import MetricsGrid


class DashboardPage(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self.window = window
        layout = QVBoxLayout(self)
        metrics = [
            "Loaded Package", "Session Status", "Current Room", "Active Puzzles", "Solved Puzzles",
            "Active Outputs", "Active Alerts", "Timer", "Simulation Speed", "Operator Mode",
        ]
        self.metrics = MetricsGrid(metrics)
        layout.addWidget(self.metrics)
        buttons = QGridLayout()
        actions = [
            ("Load Package", lambda: self.window.show_page("Package Loader")),
            ("Start Session", self.window.engine.start_session),
            ("Pause Session", self.window.engine.pause_session),
            ("Stop Session", self.window.engine.stop_session),
            ("Reset Session", self.window.engine.stop_session),
            ("Reset Room", self.window.engine.reset_room),
            ("Emergency Unlock", lambda: self.window.engine.trigger_operator_action("Emergency Unlock All")),
            ("Open Operator Controls", lambda: self.window.show_page("Operator Controls")),
            ("Open Room View", lambda: self.window.show_page("Room View")),
        ]
        for idx, (title, callback) in enumerate(actions):
            button = QPushButton(title)
            button.clicked.connect(callback)
            buttons.addWidget(button, idx // 3, idx % 3)
        layout.addLayout(buttons)

    def refresh(self) -> None:
        engine = self.window.engine
        package = engine.package
        solved = sum(1 for puzzle in package.puzzles if puzzle.solved) if package else 0
        active = sum(1 for puzzle in package.puzzles if not puzzle.solved) if package else 0
        values = {
            "Loaded Package": package.name if package else "None",
            "Session Status": engine.session.status.title(),
            "Current Room": engine.active_room,
            "Active Puzzles": str(active),
            "Solved Puzzles": str(solved),
            "Active Outputs": str(len(engine.dispatcher.active_outputs)),
            "Active Alerts": ", ".join(engine.active_alerts) or "None",
            "Timer": str(engine.session.elapsed),
            "Simulation Speed": f"{engine.session.speed:.1f}x",
            "Operator Mode": engine.session.operator_mode,
        }
        for key, value in values.items():
            self.metrics.cards[key].set_value(value)
