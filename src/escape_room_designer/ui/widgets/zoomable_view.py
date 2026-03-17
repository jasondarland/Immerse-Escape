"""Zoom-capable QGraphicsView used by editor pages."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QGraphicsView


class ZoomableGraphicsView(QGraphicsView):
    """Graphics view with wheel zoom and helper actions."""

    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self._zoom = 0
        self._zoom_step = 1.15
        self._zoom_min = -18
        self._zoom_max = 32
        self.setRenderHints(self.renderHints() | QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    def zoom_in(self) -> None:
        if self._zoom >= self._zoom_max:
            return
        self._zoom += 1
        self.scale(self._zoom_step, self._zoom_step)

    def zoom_out(self) -> None:
        if self._zoom <= self._zoom_min:
            return
        self._zoom -= 1
        self.scale(1 / self._zoom_step, 1 / self._zoom_step)

    def zoom_reset(self) -> None:
        self.resetTransform()
        self._zoom = 0

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
            return
        super().wheelEvent(event)
