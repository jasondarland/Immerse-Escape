from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QBrush, QPen
from PySide6.QtWidgets import QComboBox, QGraphicsScene, QGraphicsView, QLabel, QVBoxLayout, QWidget


STATE_COLORS = {
    "locked": "#E63946",
    "unlocked": "#21C55D",
    "idle": "#AFC2D9",
    "armed": "#1E90FF",
    "active": "#F59E0B",
    "waiting": "#64748B",
    "inactive": "#24324A",
}


class RoomViewPage(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self.window = window
        layout = QVBoxLayout(self)
        self.room_selector = QComboBox()
        self.room_selector.currentTextChanged.connect(self._room_changed)
        self.summary = QLabel("Digital twin room map")
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.room_selector)
        layout.addWidget(self.summary)
        layout.addWidget(self.view)

    def _room_changed(self, room: str) -> None:
        if room and room != self.window.engine.active_room:
            self.window.engine.active_room = room
            self.window.refresh_all()

    def refresh(self) -> None:
        engine = self.window.engine
        package = engine.package
        self.room_selector.blockSignals(True)
        current = self.room_selector.currentText()
        self.room_selector.clear()
        rooms = [room.get("name", "Unnamed Room") for room in package.rooms] if package else []
        self.room_selector.addItems(rooms)
        selected_room = engine.active_room if engine.active_room in rooms else (current if current in rooms else rooms[0] if rooms else "")
        if selected_room:
            engine.active_room = selected_room
            self.room_selector.setCurrentText(selected_room)
        self.room_selector.blockSignals(False)
        self.scene.clear()
        if not package or not selected_room:
            self.summary.setText("No package loaded.")
            return
        self.summary.setText(f"Viewing {selected_room} — live device state and puzzle relevance")
        room_devices = [device for device in package.devices if device.room == selected_room]
        for idx, device in enumerate(room_devices):
            x = 30 + (idx % 3) * 180
            y = 30 + (idx // 3) * 120
            color = QColor(STATE_COLORS.get(device.state, "#AFC2D9"))
            rect = self.scene.addRect(QRectF(x, y, 140, 80), QPen(QColor("#E6EEF8")), QBrush(color))
            text = self.scene.addText(f"{device.name}\n{device.kind}\n{device.state}")
            text.setDefaultTextColor(QColor("#0B1220"))
            text.setPos(x + 8, y + 8)
            rect.setToolTip(str(device.metadata))
