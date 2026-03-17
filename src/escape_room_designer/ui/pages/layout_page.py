"""Visual layout editor with object library and multi-room support."""
from __future__ import annotations

import uuid

from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from escape_room_designer.models.project_model import RoomLayout
from escape_room_designer.ui.widgets.layout_scene import LayoutScene
from escape_room_designer.ui.widgets.zoomable_view import ZoomableGraphicsView


LIBRARY = {
    "Architecture": ["Wall", "Half wall", "Door", "Hidden door", "Sliding door", "Trap door", "Window", "Mirror", "Secret panel", "Bookshelf opening", "Vent", "Ceiling hatch", "Floor hatch", "Archway", "Stair section", "Ramp", "Platform"],
    "Furniture + Scenic": ["Table", "Desk", "Chair", "Cabinet", "Dresser", "Shelf", "Bookcase", "Bed", "Crate", "Barrel", "Chest", "Workbench", "Podium", "Throne", "Locker", "Nightstand", "Sink", "Fireplace", "Wall art", "Rug", "Statue", "Fake stone", "Scenic wall flats", "Tomb", "Altar", "Control console", "Laboratory station"],
    "Puzzle Interactions": ["Push button", "Hidden button", "Toggle switch", "Key switch", "Lever", "Rotary dial", "Combination dial", "Keypad", "Touch plate", "RFID reader", "NFC point", "Magnetic reed switch", "Pressure plate", "Break beam sensor", "Motion sensor", "Laser sensor", "Photo sensor", "Microphone trigger", "Weight sensor", "Pull chain", "Rope pull", "Sliding puzzle section", "Tile puzzle panel", "Symbol input panel", "Sequence button bank", "Morse input key", "Telephone prop", "Typewriter prop", "Puzzle chest", "Lock box", "Decoder wheel station"],
    "Locks + Access": ["Mag lock", "Electric strike", "Cabinet lock", "Solenoid lock", "Latch", "Deadbolt mechanism", "Padlock prop", "Combination lock", "RFID lock", "Hidden release", "Door contact sensor", "Lock status indicator"],
    "Effects + Reveals": ["Fog machine", "Haze machine", "Fan", "Scent emitter", "Vibration motor", "Drop panel", "Pop-up mechanism", "Rotating wall", "Moving shelf", "Reveal drawer", "Secret compartment", "Pneumatic effect", "Water effect trigger", "Air blast effect", "Flash effect", "Strobe effect"],
    "Lighting": ["Practical lamp", "LED strip", "RGB strip", "DMX fixture", "PAR can", "Spot fixture", "Wash fixture", "Pixel node cluster", "Backlight fixture", "Blacklight", "Flicker light", "Emergency light", "Indicator light", "Exit sign prop"],
    "Audio + Video": ["Speaker", "Speaker zone", "Hidden speaker", "Audio player", "Screen", "Monitor", "TV prop", "Projector", "Projection surface", "Touchscreen", "Control monitor", "Video playback point", "Intercom speaker", "Telephone audio point"],
    "Control + Electronics": ["Relay board", "IO module", "Arduino node", "Raspberry Pi node", "IMMERSE Node-8", "Node-Audio", "Node-Lighting", "Node-GPIO", "Network switch", "PoE switch", "Power supply", "UPS", "Control rack", "Patch panel", "Interface box"],
    "Decorative / Game Flow": ["Start point", "Intro point", "Hint point", "Finale point", "Reset point", "Actor position", "GM observation point", "Camera", "CCTV point", "Guest flow arrow", "Staff path arrow", "Queue marker", "Safety marker"],
}


class LibraryList(QListWidget):
    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item:
            return
        mime = QMimeData()
        mime.setText(item.data(Qt.ItemDataRole.UserRole))
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.DropAction.CopyAction)


class LayoutDropView(ZoomableGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        data = event.mimeData().text().split("|", 1)
        if len(data) == 2:
            category, name = data
            pos = self.mapToScene(event.position().toPoint())
            self.scene().add_layout_object(name.lower(), pos.x(), pos.y(), name=name, category=category)
            event.acceptProposedAction()
            return
        super().dropEvent(event)


class LayoutPage(QWidget):
    def __init__(self):
        super().__init__()
        self.room_tabs = QTabWidget()
        self._scenes: dict[str, LayoutScene] = {}

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        left = QVBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search library...")
        self.search.textChanged.connect(self.populate_library)
        self.library = LibraryList()
        left.addWidget(self.search)
        left.addWidget(self.library, 1)
        self.populate_library()

        self.toolbar = QToolBar("Layout Tools")
        self.toolbar.setOrientation(Qt.Orientation.Vertical)
        self.toolbar.addAction("Add Room", self.add_room)
        self.toolbar.addAction("Remove Room", self.remove_current_room)
        self.toolbar.addAction("Set Background", self.pick_background)
        self.toolbar.addAction("Set Image", self.pick_image_for_selected)
        self.toolbar.addAction("Align Left", lambda: self.current_scene().align_selected_left())
        self.toolbar.addAction("Bring Front", lambda: self.current_scene().bring_to_front())
        self.toolbar.addAction("Send Back", lambda: self.current_scene().send_to_back())
        self.toolbar.addAction("Zoom +", lambda: self.current_view().zoom_in())
        self.toolbar.addAction("Zoom -", lambda: self.current_view().zoom_out())
        self.toolbar.addAction("Reset Zoom", lambda: self.current_view().zoom_reset())

        root.addLayout(left, 1)
        root.addWidget(self.toolbar)
        root.addWidget(self.room_tabs, 4)

        self.add_room("Room 1")

    def populate_library(self):
        q = self.search.text().strip().lower()
        self.library.clear()
        for cat, items in LIBRARY.items():
            for name in items:
                if q and q not in name.lower() and q not in cat.lower():
                    continue
                it = QListWidgetItem(f"[{cat}] {name}")
                it.setData(Qt.ItemDataRole.UserRole, f"{cat}|{name}")
                self.library.addItem(it)

    def _create_room_view(self, room_name: str, room_id: str | None = None):
        rid = room_id or str(uuid.uuid4())
        scene = LayoutScene()
        view = LayoutDropView(scene)
        view.setProperty("room_id", rid)
        self._scenes[rid] = scene
        self.room_tabs.addTab(view, room_name)
        self.room_tabs.setCurrentWidget(view)

    def add_room(self, default_name: str | None = None):
        name = default_name
        if name is None:
            name, ok = QInputDialog.getText(self, "New Room", "Room name:")
            if not ok or not name.strip():
                return
        self._create_room_view(name)

    def remove_current_room(self):
        if self.room_tabs.count() <= 1:
            return
        idx = self.room_tabs.currentIndex()
        wid = self.room_tabs.widget(idx)
        rid = wid.property("room_id")
        self.room_tabs.removeTab(idx)
        self._scenes.pop(rid, None)

    def current_view(self):
        return self.room_tabs.currentWidget()

    def current_scene(self):
        return self._scenes[self.current_view().property("room_id")]

    def pick_background(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Background Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if fn:
            self.current_scene().set_background_image(fn)

    def pick_image_for_selected(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Object Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if fn:
            self.current_scene().set_image_for_selected(fn)

    def export_rooms(self) -> list[RoomLayout]:
        rooms = []
        for i in range(self.room_tabs.count()):
            v = self.room_tabs.widget(i)
            rid = v.property("room_id")
            s = self._scenes[rid]
            rooms.append(RoomLayout(room_id=rid, room_name=self.room_tabs.tabText(i), background_image=s.background_image_path, objects=s.export_objects()))
        return rooms

    def import_rooms(self, rooms: list[RoomLayout]):
        self.room_tabs.clear()
        self._scenes = {}
        for room in rooms:
            self._create_room_view(room.room_name, room.room_id)
            self.current_scene().import_objects(room.objects, room.background_image)
        if self.room_tabs.count() == 0:
            self.add_room("Room 1")

    def copy_selection(self):
        return self.current_scene().copy_selected_payload()

    def paste_selection(self, payload):
        self.current_scene().paste_payload(payload)

    def delete_selection(self):
        self.current_scene().delete_selected()
