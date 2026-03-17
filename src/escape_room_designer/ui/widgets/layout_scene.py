"""Layout editor scene and items."""
from __future__ import annotations

import uuid

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsScene

from escape_room_designer.models.project_model import LayoutObject


class LayoutRectItem(QGraphicsRectItem):
    """Movable/resizable room object visual."""

    def __init__(self, obj: LayoutObject):
        super().__init__(0, 0, obj.width, obj.height)
        self.obj = obj
        self.setPos(obj.x, obj.y)
        self.setRotation(obj.rotation)
        self.setBrush(QBrush(QColor(obj.color)))
        self.setPen(QPen(QColor("#8ba3c7"), 1.2))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.obj.x = float(value.x())
            self.obj.y = float(value.y())
        return super().itemChange(change, value)


class LayoutScene(QGraphicsScene):
    """Scene with grid background and helper object factory."""

    def __init__(self):
        super().__init__(-2500, -2500, 5000, 5000)
        self.setBackgroundBrush(QColor("#0c1117"))

    def add_layout_object(self, object_type: str, x: float = 0, y: float = 0) -> LayoutRectItem:
        size_map = {
            "wall": (240, 20),
            "door": (80, 18),
            "prop": (70, 70),
            "sensor": (36, 36),
            "light": (30, 30),
        }
        width, height = size_map.get(object_type, (70, 70))
        obj = LayoutObject(
            object_id=str(uuid.uuid4()),
            object_type=object_type,
            name=f"{object_type.title()} {len(self.items()) + 1}",
            x=x,
            y=y,
            width=width,
            height=height,
            color="#4d6a91",
        )
        item = LayoutRectItem(obj)
        self.addItem(item)
        return item

    def export_objects(self) -> list[LayoutObject]:
        objects: list[LayoutObject] = []
        for item in self.items():
            if isinstance(item, LayoutRectItem):
                rect: QRectF = item.rect()
                item.obj.width = rect.width()
                item.obj.height = rect.height()
                item.obj.rotation = item.rotation()
                objects.append(item.obj)
        return objects

    def import_objects(self, layout_objects: list[LayoutObject]) -> None:
        self.clear()
        for obj in layout_objects:
            self.addItem(LayoutRectItem(obj))

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        painter.setPen(QPen(QColor("#19212c"), 1))
        grid_size = 40
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)
        x = left
        while x < rect.right():
            painter.drawLine(x, rect.top(), x, rect.bottom())
            x += grid_size
        y = top
        while y < rect.bottom():
            painter.drawLine(rect.left(), y, rect.right(), y)
            y += grid_size
