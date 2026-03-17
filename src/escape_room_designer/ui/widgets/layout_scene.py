"""Layout editor scene and items."""
from __future__ import annotations

import uuid
from copy import deepcopy

from PySide6.QtCore import QRectF
from PySide6.QtGui import QBrush, QColor, QPen, QPixmap
from PySide6.QtWidgets import QGraphicsItem, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsScene

from escape_room_designer.models.project_model import LayoutObject


class LayoutRectItem(QGraphicsRectItem):
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
            self.image_item = None
        if not self.obj.image_path:
            return
        pixmap = QPixmap(self.obj.image_path)
        if pixmap.isNull():
            return
        self.image_item = QGraphicsPixmapItem(pixmap.scaled(int(self.obj.width), int(self.obj.height)), self)
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
    def __init__(self):
        super().__init__(-5000, -5000, 10000, 10000)
        self.setBackgroundBrush(QColor("#0c1117"))
        self.background_image_path = ""
        self.background_item: QGraphicsPixmapItem | None = None

    def set_background_image(self, image_path: str) -> None:
        self.background_image_path = image_path
        if self.background_item:
            self.removeItem(self.background_item)
            self.background_item = None
        if image_path:
            px = QPixmap(image_path)
            if not px.isNull():
                self.background_item = QGraphicsPixmapItem(px)
                self.background_item.setZValue(-999)
                self.addItem(self.background_item)

    def add_layout_object(self, object_type: str, x: float = 0, y: float = 0, name: str | None = None, category: str = "") -> LayoutRectItem:
        size_map = {
            "wall": (240, 20), "half wall": (120, 20), "door": (80, 18), "hidden door": (80, 18), "sliding door": (100, 20),
            "trap door": (80, 80), "window": (80, 20), "mag lock": (20, 20), "keypad": (30, 50), "rfid reader": (30, 30),
            "speaker": (40, 40), "dmx fixture": (34, 34), "relay board": (50, 35), "camera": (30, 30), "prop": (70, 70),
        }
        width, height = size_map.get(object_type.lower(), (70, 70))
        obj = LayoutObject(
            object_id=str(uuid.uuid4()),
            object_type=object_type,
            name=name or f"{object_type.title()} {len(self.items()) + 1}",
            x=x,
            y=y,
            width=width,
            height=height,
            color="#4d6a91",
            metadata={"category": category, "state": "idle"},
        )
        item = LayoutRectItem(obj)
        self.addItem(item)
        return item

    def selected_layout_items(self) -> list[LayoutRectItem]:
        return [i for i in self.selectedItems() if isinstance(i, LayoutRectItem)]

    def copy_selected_payload(self) -> list[LayoutObject]:
        return [deepcopy(i.obj) for i in self.selected_layout_items()]

    def paste_payload(self, payload: list[LayoutObject], offset: int = 24) -> None:
        for obj in payload:
            c = deepcopy(obj)
            c.object_id = str(uuid.uuid4())
            c.x += offset
            c.y += offset
            self.addItem(LayoutRectItem(c))

    def delete_selected(self) -> None:
        for i in self.selected_layout_items():
            self.removeItem(i)

    def set_image_for_selected(self, image_path: str) -> None:
        for i in self.selected_layout_items():
            i.set_image(image_path)

    def align_selected_left(self) -> None:
        items = self.selected_layout_items()
        if not items:
            return
        left = min(i.pos().x() for i in items)
        for i in items:
            i.setX(left)

    def bring_to_front(self) -> None:
        zmax = max([i.zValue() for i in self.items()] + [0]) + 1
        for i in self.selected_layout_items():
            i.setZValue(zmax)

    def send_to_back(self) -> None:
        zmin = min([i.zValue() for i in self.items()] + [0]) - 1
        for i in self.selected_layout_items():
            i.setZValue(zmin)

    def export_objects(self) -> list[LayoutObject]:
        out = []
        for i in self.items():
            if isinstance(i, LayoutRectItem):
                i.obj.width = i.rect().width()
                i.obj.height = i.rect().height()
                i.obj.rotation = i.rotation()
                out.append(i.obj)
        return out

    def import_objects(self, layout_objects: list[LayoutObject], background_image: str = "") -> None:
        self.clear()
        self.background_item = None
        self.set_background_image(background_image)
        for obj in layout_objects:
            self.addItem(LayoutRectItem(obj))

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        painter.setPen(QPen(QColor("#19212c"), 1))
        step = 40
        x = int(rect.left()) - (int(rect.left()) % step)
        while x < rect.right():
            painter.drawLine(x, rect.top(), x, rect.bottom())
            x += step
        y = int(rect.top()) - (int(rect.top()) % step)
        while y < rect.bottom():
            painter.drawLine(rect.left(), y, rect.right(), y)
            y += step
