"""Visual room layout page with multi-room support."""
from __future__ import annotations

import uuid

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QTabWidget,
    QToolBar,
    QWidget,
)

from escape_room_designer.models.project_model import RoomLayout
from escape_room_designer.ui.widgets.layout_scene import LayoutScene
from escape_room_designer.ui.widgets.zoomable_view import ZoomableGraphicsView


class LayoutPage(QWidget):
    def __init__(self):
        super().__init__()
        self.room_tabs = QTabWidget()
        self._scenes: dict[str, LayoutScene] = {}

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.toolbar = QToolBar("Layout Tools")
        self.toolbar.setOrientation(Qt.Orientation.Vertical)
        self.toolbar.addAction("Add Room", self.add_room)
        self.toolbar.addAction("Remove Room", self.remove_current_room)
        self.toolbar.addSeparator()
        self.toolbar.addAction("Zoom In", lambda: self.current_view().zoom_in())
        self.toolbar.addAction("Zoom Out", lambda: self.current_view().zoom_out())
        self.toolbar.addAction("Reset Zoom", lambda: self.current_view().zoom_reset())
        self.toolbar.addSeparator()
        self.toolbar.addAction("Set Background", self.pick_background)
        self.toolbar.addAction("Set Image To Selected", self.pick_image_for_selected)
        self.toolbar.addSeparator()
        self.toolbar.addAction("Add Wall", lambda: self.current_scene().add_layout_object("wall", 20, 20))
        self.toolbar.addAction("Add Door", lambda: self.current_scene().add_layout_object("door", 40, 40))
        self.toolbar.addAction("Add Prop", lambda: self.current_scene().add_layout_object("prop", 60, 60))
        self.toolbar.addAction("Add Sensor", lambda: self.current_scene().add_layout_object("sensor", 90, 90))
        self.toolbar.addAction("Add Light", lambda: self.current_scene().add_layout_object("light", 120, 120))

        layout.addWidget(self.toolbar)
        layout.addWidget(self.room_tabs, 1)

        self.add_room("Room 1")

    def _create_room_view(self, room_name: str, room_id: str | None = None) -> None:
        rid = room_id or str(uuid.uuid4())
        scene = LayoutScene()
        view = ZoomableGraphicsView(scene)
        self._scenes[rid] = scene
        self.room_tabs.addTab(view, room_name)
        self.room_tabs.setCurrentWidget(view)
        view.setProperty("room_id", rid)

    def add_room(self, default_name: str | None = None) -> None:
        name = default_name
        if name is None:
            name, ok = QInputDialog.getText(self, "New Room", "Room name:")
            if not ok or not name.strip():
                return
        self._create_room_view(name)

    def remove_current_room(self) -> None:
        if self.room_tabs.count() <= 1:
            return
        idx = self.room_tabs.currentIndex()
        widget = self.room_tabs.widget(idx)
        room_id = widget.property("room_id")
        self.room_tabs.removeTab(idx)
        if room_id in self._scenes:
            del self._scenes[room_id]

    def current_view(self) -> ZoomableGraphicsView:
        return self.room_tabs.currentWidget()

    def current_scene(self) -> LayoutScene:
        room_id = self.current_view().property("room_id")
        return self._scenes[room_id]

    def pick_background(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Background Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if filename:
            self.current_scene().set_background_image(filename)

    def pick_image_for_selected(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Object Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if filename:
            self.current_scene().set_image_for_selected(filename)

    def export_rooms(self) -> list[RoomLayout]:
        rooms: list[RoomLayout] = []
        for i in range(self.room_tabs.count()):
            view = self.room_tabs.widget(i)
            room_id = view.property("room_id")
            scene = self._scenes[room_id]
            rooms.append(
                RoomLayout(
                    room_id=room_id,
                    room_name=self.room_tabs.tabText(i),
                    background_image=scene.background_image_path,
                    objects=scene.export_objects(),
                )
            )
        return rooms

    def import_rooms(self, rooms: list[RoomLayout]) -> None:
        self.room_tabs.clear()
        self._scenes = {}
        for room in rooms:
            self._create_room_view(room.room_name, room.room_id)
            scene = self.current_scene()
            scene.import_objects(room.objects, room.background_image)
        if self.room_tabs.count() == 0:
            self.add_room("Room 1")

    def copy_selection(self):
        return self.current_scene().copy_selected_payload()

    def paste_selection(self, payload):
        self.current_scene().paste_payload(payload)

    def delete_selection(self):
        self.current_scene().delete_selected()
