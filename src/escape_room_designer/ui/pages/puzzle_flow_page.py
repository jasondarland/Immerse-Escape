"""Puzzle flow graph editor page."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsView, QHBoxLayout, QToolBar, QWidget

from escape_room_designer.ui.widgets.node_scene import NodeScene


class PuzzleFlowPage(QWidget):
    def __init__(self):
        super().__init__()
        self.scene = NodeScene()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QToolBar("Puzzle Flow")
        toolbar.setOrientation(Qt.Orientation.Vertical)
        toolbar.addAction("Add Puzzle", lambda: self.scene.add_node("puzzle", "New Puzzle", 0, 0))
        toolbar.addAction("Add Hint", lambda: self.scene.add_node("hint", "Hint Moment", 220, 80))
        toolbar.addAction("Connect Selected", self.scene.connect_selected)

        self.view = QGraphicsView(self.scene)
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

        layout.addWidget(toolbar)
        layout.addWidget(self.view, 1)
