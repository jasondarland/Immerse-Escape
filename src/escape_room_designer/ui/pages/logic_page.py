"""Logic and trigger editor framework page."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsView, QHBoxLayout, QToolBar, QWidget

from escape_room_designer.ui.widgets.node_scene import NodeScene


class LogicPage(QWidget):
    def __init__(self):
        super().__init__()
        self.scene = NodeScene()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QToolBar("Logic Builder")
        toolbar.setOrientation(Qt.Orientation.Vertical)
        toolbar.addAction("Input", lambda: self.scene.add_node("input", "Button Press", 20, 20))
        toolbar.addAction("AND", lambda: self.scene.add_node("logic", "AND Gate", 260, 40))
        toolbar.addAction("Delay", lambda: self.scene.add_node("logic", "Delay", 260, 150))
        toolbar.addAction("Output", lambda: self.scene.add_node("output", "Unlock Maglock", 520, 70))
        toolbar.addAction("Connect Selected", self.scene.connect_selected)

        self.view = QGraphicsView(self.scene)
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

        layout.addWidget(toolbar)
        layout.addWidget(self.view, 1)
