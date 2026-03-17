"""Layout editor scene and items."""
from __future__ import annotations

import uuid
from copy import deepcopy

from PySide6.QtCore import QRectF
from PySide6.QtGui import QBrush, QColor, QPen, QPixmap
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
)

from escape_room_designer.models.project_model import LayoutObject


class LayoutRectItem(QGraphicsRectItem):
    """Movable room object visual that can optionally show an image texture."""

    def __init__(self, obj: LayoutObject):
        super().__init__(0, 0, obj.width, obj.height)
        self.obj = obj
        self.image_item: QGraphicsPixmapItem | None = None
        self.setPos(obj.x, obj.y)
        self.setRotation(obj.rotation)
        self.setBrush(QBrush(QColor(obj.color)))
        self.setPen(QPen(QColor("#8ba3c7"), 1.2))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self._apply_image()

    def _apply_image(self) -> None:
        if self.image_item:
            self.image_item.setParentItem(None)
            self.scene().removeItem(self.image_item) if self.scene() else None
            self.image_item = None
        if not self.obj.image_path:
            return
        pixmap = QPixmap(self.obj.image_path)
        if pixmap.isNull():
            return
        scaled = pixmap.scaled(int(self.obj.width), int(self.obj.height))
        self.image_item = QGraphicsPixmapItem(scaled, self)
        self.image_item.setPos(0, 0)

    def set_image(self, image_path: str) -> None:
        self.obj.image_path = image_path
        self._apply_image()

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
        self.background_image_path: str = ""
        self.background_item: QGraphicsPixmapItem | None = None

    def set_background_image(self, image_path: str) -> None:
        self.background_image_path = image_path
        if self.background_item:
            self.removeItem(self.background_item)
            self.background_item = None
        if not image_path:
            return
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            return
        self.background_item = QGraphicsPixmapItem(pixmap)
        self.background_item.setZValue(-999)
        self.addItem(self.background_item)

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

    def selected_layout_items(self) -> list[LayoutRectItem]:
        return [item for item in self.selectedItems() if isinstance(item, LayoutRectItem)]

    def copy_selected_payload(self) -> list[LayoutObject]:
        return [deepcopy(item.obj) for item in self.selected_layout_items()]

    def paste_payload(self, payload: list[LayoutObject], offset: int = 24) -> None:
        for obj in payload:
            copied = deepcopy(obj)
            copied.object_id = str(uuid.uuid4())
            copied.x += offset
            copied.y += offset
            self.addItem(LayoutRectItem(copied))

    def delete_selected(self) -> None:
        for item in self.selected_layout_items():
            self.removeItem(item)

    def set_image_for_selected(self, image_path: str) -> None:
        for item in self.selected_layout_items():
            item.set_image(image_path)

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

    def import_objects(self, layout_objects: list[LayoutObject], background_image: str = "") -> None:
        self.clear()
        self.background_item = None
        self.set_background_image(background_image)
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
