"""Dashboard home page with actionable widgets."""
from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QGroupBox, QHBoxLayout, QLabel, QListWidget, QPushButton, QVBoxLayout, QWidget


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.on_open_page = None

        root = QVBoxLayout(self)
        actions = QHBoxLayout()
        self.new_btn = QPushButton("Create New Project")
        self.open_btn = QPushButton("Open Project")
        actions.addWidget(self.new_btn)
        actions.addWidget(self.open_btn)
        actions.addStretch()
        root.addLayout(actions)

        grid = QGridLayout()
        self.summary = QLabel("Projects: 0 | Rooms: 0 | Devices: 0 | Puzzles: 0 | Media: 0")
        self.validation = QListWidget()
        self.recent_projects = QListWidget()
        self.recent_exports = QListWidget()
        self.activity = QListWidget()
        self.rooms = QListWidget()
        self.continue_cards = QListWidget()

        grid.addWidget(self._box("Project Status Summary", self.summary), 0, 0, 1, 2)
        grid.addWidget(self._box("Validation Warnings", self.validation), 1, 0)
        grid.addWidget(self._box("Recent Projects", self.recent_projects), 1, 1)
        grid.addWidget(self._box("Recent Exports", self.recent_exports), 1, 2)
        grid.addWidget(self._box("Latest Activity Log", self.activity), 2, 0)
        grid.addWidget(self._box("Rooms/Scenes Overview", self.rooms), 2, 1)
        grid.addWidget(self._box("Continue Working", self.continue_cards), 2, 2)
        root.addLayout(grid)

        self.continue_cards.itemClicked.connect(lambda _: self._jump("Layout"))
        self.rooms.itemClicked.connect(lambda _: self._jump("Layout"))
        self.recent_exports.itemClicked.connect(lambda _: self._jump("Reports"))

    def _box(self, title, child):
        b = QGroupBox(title)
        l = QVBoxLayout(b)
        l.addWidget(child)
        return b

    def _jump(self, page):
        if self.on_open_page:
            self.on_open_page(page)

    def bind_project(self, project, validation_issues: list[str]):
        self.summary.setText(
            f"Project: {project.name} | Rooms: {len(project.layouts)} | Devices: {len(project.devices)} | "
            f"Puzzles: {len(project.puzzle_nodes)} | Media: {len(project.media)}"
        )
        self.validation.clear(); self.validation.addItems(validation_issues or ["No active warnings"])
        self.recent_projects.clear(); self.recent_projects.addItems([project.name])
        self.recent_exports.clear(); self.recent_exports.addItems([e.get("file", "No exports yet") for e in project.recent_exports] or ["No exports yet"])
        self.activity.clear(); self.activity.addItems(project.activity_log[-20:] or ["No activity yet"])
        self.rooms.clear(); self.rooms.addItems([r.room_name for r in project.layouts])
        self.continue_cards.clear(); self.continue_cards.addItems(["Continue Layout Design", "Continue Logic Programming", "Continue Timeline Authoring"])
