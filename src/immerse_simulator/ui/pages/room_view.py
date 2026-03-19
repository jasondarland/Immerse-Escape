from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QBrush, QPen, QPixmap
from PySide6.QtWidgets import QFileDialog, QComboBox, QGraphicsScene, QGraphicsView, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


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
        controls = QHBoxLayout()
        self.room_selector = QComboBox()
        self.room_selector.currentTextChanged.connect(self._room_changed)
        self.upload_button = QPushButton("Upload Background")
        self.upload_button.clicked.connect(self._upload_background)
        self.clear_button = QPushButton("Clear Background")
        self.clear_button.clicked.connect(self._clear_background)
        controls.addWidget(self.room_selector, 1)
        controls.addWidget(self.upload_button)
        controls.addWidget(self.clear_button)
        self.summary = QLabel("Digital twin room map")
        self.background_label = QLabel("Background: none")
        self.background_label.setProperty("role", "secondary")
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(self.view.renderHints())
        layout.addLayout(controls)
        layout.addWidget(self.summary)
        layout.addWidget(self.background_label)
        layout.addWidget(self.view)

    def _room_changed(self, room: str) -> None:
        if room and room != self.window.engine.active_room:
            self.window.engine.active_room = room
            self.window.refresh_all()

    def _upload_background(self) -> None:
        room = self.window.engine.active_room
        path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select background for {room}",
            str(Path.home()),
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)",
        )
        if path:
            self.window.engine.set_room_background(room, path)

    def _clear_background(self) -> None:
        room = self.window.engine.active_room
        self.window.engine.set_room_background(room, None)

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
            self.background_label.setText("Background: none")
            return

        self.summary.setText(f"Viewing {selected_room} — live device state and puzzle relevance")
        background_path = engine.get_room_background(selected_room)
        self.background_label.setText(f"Background: {Path(background_path).name}" if background_path else "Background: none")
        if background_path:
            pixmap = QPixmap(background_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(1200, 700, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.scene.addPixmap(scaled).setZValue(-10)
                self.scene.setSceneRect(QRectF(scaled.rect()))
            else:
                self.background_label.setText(f"Background: failed to load ({Path(background_path).name})")
                self.scene.setSceneRect(QRectF(0, 0, 1200, 700))
        else:
            self.scene.setSceneRect(QRectF(0, 0, 1200, 700))

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
