"""Layout editor scene and interactive layout items."""
from __future__ import annotations

import math
import uuid
from copy import deepcopy

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
)

from escape_room_designer.models.project_model import LayoutObject


STYLE_BY_TYPE = {
    "wall": (QColor("#6f7f94"), (240, 20)),
    "half wall": (QColor("#7386a0"), (120, 20)),
    "door": (QColor("#8f6f52"), (80, 18)),
    "hidden door": (QColor("#5b4f46"), (80, 18)),
    "sliding door": (QColor("#886f4f"), (100, 18)),
    "trap door": (QColor("#705f4d"), (80, 80)),
    "keypad": (QColor("#3f6d96"), (34, 50)),
    "rfid reader": (QColor("#3d7f8c"), (34, 34)),
    "mag lock": (QColor("#7c5f8f"), (24, 24)),
    "speaker": (QColor("#4f7692"), (40, 40)),
    "speaker zone": (QColor("#4f7692"), (50, 32)),
    "dmx fixture": (QColor("#916d43"), (34, 34)),
    "practical lamp": (QColor("#b58e45"), (26, 46)),
    "motion sensor": (QColor("#4f8d67"), (30, 30)),
    "break beam sensor": (QColor("#4f8d67"), (24, 24)),
    "camera": (QColor("#5c6f87"), (30, 30)),
    "relay board": (QColor("#4c5f7e"), (56, 36)),
}


class LayoutRectItem(QGraphicsRectItem):
    """Editable object item with move/resize/rotate interactions."""

    def __init__(self, obj: LayoutObject):
        default_color, default_size = STYLE_BY_TYPE.get(obj.object_type.lower(), (QColor("#4d6a91"), (70, 70)))
        if obj.width <= 0 or obj.height <= 0:
            obj.width, obj.height = default_size
        if not obj.color:
            obj.color = default_color.name()

        super().__init__(0, 0, obj.width, obj.height)
        self.obj = obj
        self.image_item: QGraphicsPixmapItem | None = None
        self.title_item = QGraphicsSimpleTextItem(self.obj.name, self)
        self.resize_handle = QGraphicsRectItem(0, 0, 10, 10, self)
        self.rotate_handle = QGraphicsEllipseItem(0, 0, 12, 12, self)

        self._is_resizing = False
        self._is_rotating = False
        self._start_rect = QRectF()
        self._start_pos = QPointF()
        self._snap = True

        self.setPos(obj.x, obj.y)
        self.setRotation(obj.rotation)
        self.setBrush(QBrush(QColor(obj.color)))
        self.setPen(QPen(QColor("#9ab8df"), 1.4))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self._apply_image()
        self._refresh_overlays()

    def _refresh_overlays(self) -> None:
        self.title_item.setText(self.obj.name)
        self.title_item.setPos(2, -18)
        self.title_item.setBrush(QColor("#e6eefb"))
        self.resize_handle.setRect(self.rect().width() - 10, self.rect().height() - 10, 10, 10)
        self.resize_handle.setBrush(QBrush(QColor("#d0e2ff")))
        self.resize_handle.setPen(QPen(QColor("#2b3f5f"), 1))
        self.rotate_handle.setRect(self.rect().width() / 2 - 6, -24, 12, 12)
        self.rotate_handle.setBrush(QBrush(QColor("#ffd58a")))
        self.rotate_handle.setPen(QPen(QColor("#3e2d14"), 1))

    def _apply_image(self) -> None:
        if self.image_item:
            self.image_item.setParentItem(None)
            self.image_item = None
        if not self.obj.image_path:
            return
        pixmap = QPixmap(self.obj.image_path)
        if pixmap.isNull():
            return
        self.image_item = QGraphicsPixmapItem(pixmap.scaled(int(self.rect().width()), int(self.rect().height())), self)
        self.image_item.setPos(0, 0)

    def set_image(self, image_path: str) -> None:
        self.obj.image_path = image_path
        self._apply_image()

    def set_snap(self, value: bool) -> None:
        self._snap = value

    def _snap_point(self, p: QPointF) -> QPointF:
        if not self._snap:
            return p
        grid = 20
        return QPointF(round(p.x() / grid) * grid, round(p.y() / grid) * grid)

    def mousePressEvent(self, event):
        local = event.position()
        if self.resize_handle.rect().contains(local):
            self._is_resizing = True
            self._start_rect = self.rect()
            self._start_pos = local
            event.accept()
            return
        if self.rotate_handle.rect().contains(local):
            self._is_rotating = True
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_resizing:
            delta = event.position() - self._start_pos
            new_w = max(12, self._start_rect.width() + delta.x())
            new_h = max(12, self._start_rect.height() + delta.y())
            self.setRect(0, 0, new_w, new_h)
            self.obj.width = new_w
            self.obj.height = new_h
            self._refresh_overlays()
            self._apply_image()
            event.accept()
            return
        if self._is_rotating:
            center = self.rect().center()
            vec = event.position() - center
            angle = math.degrees(math.atan2(vec.y(), vec.x()))
            self.setRotation(angle)
            self.obj.rotation = angle
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._is_resizing = False
        self._is_rotating = False
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            return self._snap_point(value)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.obj.x = float(value.x())
            self.obj.y = float(value.y())
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged and self.scene():
            self.scene().notify_selection_changed()
        return super().itemChange(change, value)


class LayoutScene(QGraphicsScene):
    selected_object_changed = Signal(object)

    def __init__(self):
        super().__init__(-5000, -5000, 10000, 10000)
        self.setBackgroundBrush(QColor("#0c1117"))
        self.background_image_path = ""
        self.background_item: QGraphicsPixmapItem | None = None
        self.snap_enabled = True

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

    def notify_selection_changed(self):
        selected = self.selected_layout_items()
        self.selected_object_changed.emit(selected[0].obj if selected else None)

    def add_layout_object(self, object_type: str, x: float = 0, y: float = 0, name: str | None = None, category: str = "") -> LayoutRectItem:
        color, size = STYLE_BY_TYPE.get(object_type.lower(), (QColor("#4d6a91"), (70, 70)))
        obj = LayoutObject(
            object_id=str(uuid.uuid4()),
            object_type=object_type,
            name=name or f"{object_type.title()} {len(self.items()) + 1}",
            x=x,
            y=y,
            width=size[0],
            height=size[1],
            color=color.name(),
            metadata={"category": category, "state": "idle", "subtype": name or object_type, "z_order": 0, "notes": "", "linked_device_id": "", "linked_puzzle_id": ""},
        )
        item = LayoutRectItem(obj)
        item.set_snap(self.snap_enabled)
        self.addItem(item)
        self.notify_selection_changed()
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
            item = LayoutRectItem(c)
            item.set_snap(self.snap_enabled)
            self.addItem(item)
        self.notify_selection_changed()

    def delete_selected(self) -> None:
        for i in self.selected_layout_items():
            self.removeItem(i)
        self.notify_selection_changed()

    def duplicate_selected(self) -> None:
        self.paste_payload(self.copy_selected_payload(), 28)

    def set_image_for_selected(self, image_path: str) -> None:
        for i in self.selected_layout_items():
            i.set_image(image_path)
        self.notify_selection_changed()

    def align_selected_left(self) -> None:
        items = self.selected_layout_items()
        if not items:
            return
        left = min(i.pos().x() for i in items)
        for i in items:
            i.setX(left)
        self.notify_selection_changed()

    def bring_to_front(self) -> None:
        zmax = max([i.zValue() for i in self.items()] + [0]) + 1
        for i in self.selected_layout_items():
            i.setZValue(zmax)
            i.obj.metadata["z_order"] = zmax
        self.notify_selection_changed()

    def send_to_back(self) -> None:
        zmin = min([i.zValue() for i in self.items()] + [0]) - 1
        for i in self.selected_layout_items():
            i.setZValue(zmin)
            i.obj.metadata["z_order"] = zmin
        self.notify_selection_changed()

    def set_snap(self, enabled: bool) -> None:
        self.snap_enabled = enabled
        for i in self.items():
            if isinstance(i, LayoutRectItem):
                i.set_snap(enabled)

    def update_selected_property(self, key: str, value: str) -> None:
        item = self.selected_layout_items()[0] if self.selected_layout_items() else None
        if not item:
            return
        if key == "name":
            item.obj.name = value
            item._refresh_overlays()
        elif key in {"x", "y", "width", "height", "rotation"}:
            try:
                num = float(value)
            except ValueError:
                return
            if key == "x":
                item.setX(num)
            elif key == "y":
                item.setY(num)
            elif key == "width":
                item.setRect(0, 0, max(12, num), item.rect().height())
                item.obj.width = item.rect().width()
            elif key == "height":
                item.setRect(0, 0, item.rect().width(), max(12, num))
                item.obj.height = item.rect().height()
            elif key == "rotation":
                item.setRotation(num)
                item.obj.rotation = num
            item._refresh_overlays()
            item._apply_image()
        else:
            item.obj.metadata[key] = value
        self.notify_selection_changed()

    def export_objects(self) -> list[LayoutObject]:
        out: list[LayoutObject] = []
        for i in self.items():
            if isinstance(i, LayoutRectItem):
                i.obj.width = i.rect().width()
                i.obj.height = i.rect().height()
                i.obj.rotation = i.rotation()
                i.obj.metadata["z_order"] = i.zValue()
                out.append(i.obj)
        return out

    def import_objects(self, layout_objects: list[LayoutObject], background_image: str = "") -> None:
        self.clear()
        self.background_item = None
        self.set_background_image(background_image)
        for obj in layout_objects:
            it = LayoutRectItem(obj)
            it.set_snap(self.snap_enabled)
            it.setZValue(float(obj.metadata.get("z_order", 0)))
            self.addItem(it)
        self.notify_selection_changed()

    def drawBackground(self, painter: QPainter, rect):
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
