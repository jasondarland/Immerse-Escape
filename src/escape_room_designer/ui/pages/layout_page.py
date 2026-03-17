"""Visual room layout page."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QGraphicsView, QHBoxLayout, QToolBar, QWidget

from escape_room_designer.ui.widgets.layout_scene import LayoutScene


class LayoutPage(QWidget):
    def __init__(self):
        super().__init__()
        self.scene = LayoutScene()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.toolbar = QToolBar("Layout Tools")
        self.toolbar.setOrientation(Qt.Orientation.Vertical)
        self.toolbar.addAction("Add Wall", lambda: self.scene.add_layout_object("wall", 20, 20))
        self.toolbar.addAction("Add Door", lambda: self.scene.add_layout_object("door", 40, 40))
        self.toolbar.addAction("Add Prop", lambda: self.scene.add_layout_object("prop", 60, 60))
        self.toolbar.addAction("Add Sensor", lambda: self.scene.add_layout_object("sensor", 90, 90))
        self.toolbar.addAction("Add Light", lambda: self.scene.add_layout_object("light", 120, 120))

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(self.view.renderHints() | QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.view, 1)
