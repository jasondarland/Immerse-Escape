"""Puzzle flow graph editor page."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QToolBar, QWidget

from escape_room_designer.ui.widgets.node_scene import NodeScene
from escape_room_designer.ui.widgets.zoomable_view import ZoomableGraphicsView


class PuzzleFlowPage(QWidget):
    def __init__(self):
        super().__init__()
        self.scene = NodeScene()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QToolBar("Puzzle Flow")
        toolbar.setOrientation(Qt.Orientation.Vertical)
        toolbar.addAction("Zoom In", self.zoom_in)
        toolbar.addAction("Zoom Out", self.zoom_out)
        toolbar.addAction("Reset Zoom", self.zoom_reset)
        toolbar.addSeparator()
        toolbar.addAction("Add Puzzle", lambda: self.scene.add_node("puzzle", "New Puzzle", 0, 0))
        toolbar.addAction("Add Hint", lambda: self.scene.add_node("hint", "Hint Moment", 220, 80))
        toolbar.addAction("Connect Selected", self.scene.connect_selected)

        self.view = ZoomableGraphicsView(self.scene)

        layout.addWidget(toolbar)
        layout.addWidget(self.view, 1)

    def zoom_in(self):
        self.view.zoom_in()

    def zoom_out(self):
        self.view.zoom_out()

    def zoom_reset(self):
        self.view.zoom_reset()

    def copy_selection(self):
        return self.scene.copy_selected_payload()

    def paste_selection(self, payload):
        self.scene.paste_payload(payload)

    def delete_selection(self):
        self.scene.delete_selected()
