from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .models import Severity, ShowElement
from .services import MockCommandService


class MainWindow(QMainWindow):
    def __init__(self, service: MockCommandService) -> None:
        super().__init__()
        self.service = service
        self.selected_room_id = "lab_a"
        self.selected_element_id = ""

        self.setWindowTitle("IMMERSE Remote OCC – Escape Room Operator")
        self.resize(1560, 930)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.operator_tab = QWidget()
        self.elements_tab = QWidget()
        self.tabs.addTab(self.operator_tab, "Operator Controls")
        self.tabs.addTab(self.elements_tab, "Show Elements / Effects")

        self._build_operator_tab()
        self._build_elements_tab()

        self.service.state_changed.connect(self.refresh)
        self.service.event_added.connect(self._append_event)
        self.refresh()

    def _build_operator_tab(self) -> None:
        root = QVBoxLayout(self.operator_tab)

        top_bar = QHBoxLayout()
        self.room_selector = QComboBox()
        for room in self.service.state.rooms.values():
            self.room_selector.addItem(room.name, room.id)
        self.room_selector.currentIndexChanged.connect(self._room_changed)

        self.timer_label = QLabel("00:00")
        self.global_status_label = QLabel("READY")
        top_bar.addWidget(QLabel("Room:"))
        top_bar.addWidget(self.room_selector)
        top_bar.addWidget(QLabel("Game Timer:"))
        top_bar.addWidget(self.timer_label)
        top_bar.addStretch()
        top_bar.addWidget(QLabel("Room Status:"))
        top_bar.addWidget(self.global_status_label)
        self.load_pack_button = QPushButton("Load ImmersePack ZIP")
        self.load_pack_button.clicked.connect(self._load_pack_zip)
        top_bar.addWidget(self.load_pack_button)
        root.addLayout(top_bar)

        splitter = QSplitter(Qt.Horizontal)
        root.addWidget(splitter, 1)

        left = QWidget()
        center = QWidget()
        right = QWidget()
        splitter.addWidget(left)
        splitter.addWidget(center)
        splitter.addWidget(right)
        splitter.setSizes([340, 600, 500])

        left_layout = QVBoxLayout(left)
        controls_box = QGroupBox("Core Controls")
        controls_grid = QGridLayout(controls_box)
        self._add_command_button(controls_grid, "Start Game", 0, 0, style="success")
        self._add_command_button(controls_grid, "Pause Game", 0, 1)
        self._add_command_button(controls_grid, "Resume Game", 1, 0)
        self._add_command_button(controls_grid, "Stop Game", 1, 1, style="danger")
        self._add_command_button(controls_grid, "Reset Room", 2, 0)
        self._add_command_button(controls_grid, "Full Reset", 2, 1, confirm=True, style="danger")
        self._add_command_button(controls_grid, "Skip Puzzle", 3, 0)
        self._add_command_button(controls_grid, "Trigger Hint", 3, 1)
        self._add_command_button(controls_grid, "Trigger Custom Hint 1", 4, 0)
        self._add_command_button(controls_grid, "Trigger Custom Hint 2", 4, 1)
        self._add_command_button(controls_grid, "Trigger Finale", 5, 0, confirm=True)
        left_layout.addWidget(controls_box)

        workflow_box = QGroupBox("Operator Workflow")
        wf_layout = QVBoxLayout(workflow_box)
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Operator notes...")
        self.notes_edit.textChanged.connect(self._save_notes)
        self.issue_edit = QLineEdit()
        self.issue_edit.setPlaceholderText("Active issue / flag")
        self.issue_edit.editingFinished.connect(self._save_issue)
        self.reset_checklist = QListWidget()
        wf_layout.addWidget(QLabel("Notes"))
        wf_layout.addWidget(self.notes_edit)
        wf_layout.addWidget(QLabel("Active Issue Tracker"))
        wf_layout.addWidget(self.issue_edit)
        wf_layout.addWidget(QLabel("Room Reset Checklist"))
        wf_layout.addWidget(self.reset_checklist)
        left_layout.addWidget(workflow_box)

        center_layout = QVBoxLayout(center)
        self.puzzle_table = QTableWidget(0, 2)
        self.puzzle_table.setHorizontalHeaderLabels(["Puzzle", "Status"])
        self.puzzle_table.horizontalHeader().setStretchLastSection(True)
        center_layout.addWidget(self._wrap("Puzzle Progress", self.puzzle_table))

        self.room_health_list = QListWidget()
        center_layout.addWidget(self._wrap("Room State Overview", self.room_health_list))

        self.alerts_list = QListWidget()
        center_layout.addWidget(self._wrap("Operator Alerts / Warnings", self.alerts_list))

        right_layout = QVBoxLayout(right)
        self.device_status_table = QTableWidget(0, 3)
        self.device_status_table.setHorizontalHeaderLabels(["System", "Device", "State"])
        self.device_status_table.horizontalHeader().setStretchLastSection(True)
        right_layout.addWidget(self._wrap("Door / Lock / Media / Lighting Status", self.device_status_table))

        self.event_log = QListWidget()
        right_layout.addWidget(self._wrap("Event Log", self.event_log))

        emergency = QGroupBox("Emergency Strip")
        em_layout = QGridLayout(emergency)
        self._add_command_button(em_layout, "Emergency Unlock All", 0, 0, confirm=True, style="danger")
        self._add_command_button(em_layout, "Lock All Doors", 0, 1)
        self._add_command_button(em_layout, "Stop All Audio", 0, 2)
        self._add_command_button(em_layout, "Stop All Video", 0, 3)
        self._add_command_button(em_layout, "Blackout / Kill Effects", 1, 0, confirm=True, style="danger")
        self._add_command_button(em_layout, "Restore Default State", 1, 1)
        root.addWidget(emergency)

    def _build_elements_tab(self) -> None:
        root = QVBoxLayout(self.elements_tab)

        top = QHBoxLayout()
        self.element_room_filter = QComboBox()
        self.element_room_filter.addItem("All Rooms", "all")
        for room in self.service.state.rooms.values():
            self.element_room_filter.addItem(room.name, room.id)
        self.element_room_filter.currentIndexChanged.connect(self.refresh_elements)

        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        for c in [
            "Doors / Locks",
            "Audio",
            "Video",
            "Lighting",
            "Effects",
            "Props / Mechanisms",
            "Hints / Clues",
            "Scenic Triggers",
            "Utility / Overrides",
        ]:
            self.category_filter.addItem(c)
        self.category_filter.currentIndexChanged.connect(self.refresh_elements)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search cue name...")
        self.search.textChanged.connect(self.refresh_elements)

        top.addWidget(QLabel("Room Filter:"))
        top.addWidget(self.element_room_filter)
        top.addWidget(QLabel("Category:"))
        top.addWidget(self.category_filter)
        top.addWidget(self.search)
        root.addLayout(top)

        splitter = QSplitter(Qt.Horizontal)
        root.addWidget(splitter, 1)

        left = QWidget()
        mid = QWidget()
        right = QWidget()
        splitter.addWidget(left)
        splitter.addWidget(mid)
        splitter.addWidget(right)
        splitter.setSizes([280, 820, 420])

        left_layout = QVBoxLayout(left)
        self.rooms_list = QListWidget()
        self.rooms_list.itemSelectionChanged.connect(self._room_list_selected)
        for room in self.service.state.rooms.values():
            self.rooms_list.addItem(room.name)
        self.critical_cues = QListWidget()
        for name in ["Emergency Unlock All", "Trigger Finale", "Blackout / Kill Effects"]:
            self.critical_cues.addItem(name)
        left_layout.addWidget(self._wrap("Rooms / Zones", self.rooms_list))
        left_layout.addWidget(self._wrap("Favorites / Critical Cues", self.critical_cues))

        mid_layout = QVBoxLayout(mid)
        self.elements_table = QTableWidget(0, 5)
        self.elements_table.setHorizontalHeaderLabels(["Cue", "Room", "Category", "Status", "Fire"])
        self.elements_table.horizontalHeader().setStretchLastSection(False)
        self.elements_table.itemSelectionChanged.connect(self._element_selected)
        mid_layout.addWidget(self._wrap("Trigger Grid", self.elements_table))

        right_layout = QVBoxLayout(right)
        self.details = QTextEdit()
        self.details.setReadOnly(True)
        right_layout.addWidget(self._wrap("Selected Element Details", self.details))

    def _add_command_button(
        self,
        layout: QGridLayout,
        label: str,
        row: int,
        col: int,
        confirm: bool = False,
        style: str = "",
    ) -> None:
        btn = QPushButton(label)
        if style:
            btn.setObjectName(style)
            btn.style().polish(btn)

        def on_click() -> None:
            room_id = self.selected_room_id
            if confirm:
                ok = QMessageBox.question(self, "Confirm Action", f"Execute '{label}' for selected scope?")
                if ok != QMessageBox.Yes:
                    return
            self.service.execute(room_id, label)

        btn.clicked.connect(on_click)
        layout.addWidget(btn, row, col)

    def _room_changed(self) -> None:
        self._save_notes()
        room_id = self.room_selector.currentData()
        if not room_id:
            return
        self.selected_room_id = room_id
        room = self.service.state.rooms[self.selected_room_id]
        self.notes_edit.setPlainText(room.notes)
        self.refresh()

    def _load_pack_zip(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Immerse Pack ZIP",
            "",
            "ZIP files (*.zip)",
        )
        if not file_path:
            return

        try:
            self.service.load_pack(file_path)
            self._rebuild_room_controls()
            self.refresh()
        except Exception as exc:
            QMessageBox.critical(self, "Load Pack Failed", str(exc))

    def _rebuild_room_controls(self) -> None:
        room_ids = list(self.service.state.rooms.keys())
        if not room_ids:
            return

        self.selected_room_id = room_ids[0]

        self.room_selector.blockSignals(True)
        self.room_selector.clear()
        for room in self.service.state.rooms.values():
            self.room_selector.addItem(room.name, room.id)
        self.room_selector.setCurrentIndex(0)
        self.room_selector.blockSignals(False)

        self.element_room_filter.blockSignals(True)
        self.element_room_filter.clear()
        self.element_room_filter.addItem("All Rooms", "all")
        for room in self.service.state.rooms.values():
            self.element_room_filter.addItem(room.name, room.id)
        self.element_room_filter.setCurrentIndex(0)
        self.element_room_filter.blockSignals(False)

        self.rooms_list.blockSignals(True)
        self.rooms_list.clear()
        for room in self.service.state.rooms.values():
            self.rooms_list.addItem(room.name)
        self.rooms_list.blockSignals(False)

    def _save_notes(self) -> None:
        if self.selected_room_id not in self.service.state.rooms:
            return
        room = self.service.state.rooms[self.selected_room_id]
        room.notes = self.notes_edit.toPlainText().strip()

    def _save_issue(self) -> None:
        if self.selected_room_id not in self.service.state.rooms:
            return
        room = self.service.state.rooms[self.selected_room_id]
        room.active_issue = self.issue_edit.text().strip()
        if room.active_issue:
            self.service.execute(room.id, "Issue Flag Updated", room.active_issue)

    def _room_list_selected(self) -> None:
        item = self.rooms_list.currentItem()
        if not item:
            return
        idx = self.element_room_filter.findText(item.text())
        if idx >= 0:
            self.element_room_filter.setCurrentIndex(idx)

    def _element_selected(self) -> None:
        row = self.elements_table.currentRow()
        if row < 0:
            return
        item = self.elements_table.item(row, 0)
        if not item:
            return
        element_id = item.data(Qt.UserRole)
        if not element_id:
            return
        if element_id not in self.service.state.show_elements:
            return
        self.selected_element_id = element_id
        el = self.service.state.show_elements[element_id]
        room = self.service.state.rooms.get(el.room_id)
        room_name = room.name if room else el.room_id
        triggered = el.last_triggered.strftime("%H:%M:%S") if el.last_triggered else "Never"
        self.details.setPlainText(
            f"Name: {el.name}\n"
            f"Room: {room_name}\n"
            f"Type: {el.category}\n"
            f"Current Status: {el.status}\n"
            f"Last Triggered: {triggered}\n"
            f"Reset Requirement: {'Yes' if el.reset_required else 'No'}\n"
            f"Auto Reset: {'Yes' if el.auto_reset else 'No'}\n"
            f"Notes: {el.notes or '-'}\n"
            f"Linked System / Device ID: {el.linked_device_id or '-'}"
        )

    def _append_event(self, event) -> None:
        sev = "⚠" if event.severity != Severity.INFO else "•"
        room = self.service.state.rooms.get(event.room_id)
        room_name = room.name if room else event.room_id
        self.event_log.insertItem(0, f"[{event.at:%H:%M:%S}] {sev} {room_name}: {event.message}")
        while self.event_log.count() > 200:
            self.event_log.takeItem(self.event_log.count() - 1)

    def refresh(self) -> None:
        if self.selected_room_id not in self.service.state.rooms:
            room_ids = list(self.service.state.rooms.keys())
            if not room_ids:
                return
            self.selected_room_id = room_ids[0]
        room = self.service.state.rooms[self.selected_room_id]
        mins, secs = divmod(room.elapsed_seconds, 60)
        self.timer_label.setText(f"{mins:02}:{secs:02}")
        self.global_status_label.setText(room.health.value.upper())
        self.global_status_label.setObjectName(f"status_{room.health.value.replace(' ', '_')}")
        self.global_status_label.style().polish(self.global_status_label)
        self.issue_edit.setText(room.active_issue)
        self._refresh_puzzles(room)
        self._refresh_room_health()
        self._refresh_alerts()
        self._refresh_devices()
        self._refresh_checklist(room)
        self.refresh_elements()

    def _refresh_puzzles(self, room) -> None:
        self.puzzle_table.setRowCount(len(room.puzzles))
        for i, p in enumerate(room.puzzles):
            self.puzzle_table.setItem(i, 0, QTableWidgetItem(p.name))
            self.puzzle_table.setItem(i, 1, QTableWidgetItem(p.status))

    def _refresh_room_health(self) -> None:
        self.room_health_list.clear()
        for room in self.service.state.rooms.values():
            self.room_health_list.addItem(f"{room.name}: {room.health.value.upper()} | Puzzle: {room.current_puzzle}")

    def _refresh_alerts(self) -> None:
        self.alerts_list.clear()
        warnings = [e for e in self.service.state.events[-20:] if e.severity != Severity.INFO]
        if not warnings:
            self.alerts_list.addItem("No active warnings")
            return
        for e in warnings:
            self.alerts_list.addItem(f"[{e.at:%H:%M:%S}] {self.service.state.rooms[e.room_id].name} - {e.message}")

    def _refresh_devices(self) -> None:
        selected = self.selected_room_id
        devices = [d for d in self.service.state.devices.values() if d.room_id == selected]
        self.device_status_table.setRowCount(len(devices))
        for i, d in enumerate(devices):
            self.device_status_table.setItem(i, 0, QTableWidgetItem(d.kind.title()))
            self.device_status_table.setItem(i, 1, QTableWidgetItem(d.name))
            self.device_status_table.setItem(i, 2, QTableWidgetItem(d.status))

    def _refresh_checklist(self, room) -> None:
        self.reset_checklist.clear()
        for item in room.reset_checklist:
            self.reset_checklist.addItem(QListWidgetItem(item))

    def refresh_elements(self) -> None:
        room_filter = self.element_room_filter.currentData() or "all"
        category_filter = self.category_filter.currentText()
        search = self.search.text().lower().strip()

        rows: list[ShowElement] = []
        for el in self.service.state.show_elements.values():
            if room_filter != "all" and el.room_id != room_filter:
                continue
            if category_filter != "All Categories" and el.category != category_filter:
                continue
            if search and search not in el.name.lower():
                continue
            rows.append(el)

        self.elements_table.blockSignals(True)
        self.elements_table.clearContents()
        self.elements_table.setRowCount(len(rows))
        for i, el in enumerate(rows):
            cue_item = QTableWidgetItem(el.name)
            cue_item.setData(Qt.UserRole, el.id)
            self.elements_table.setItem(i, 0, cue_item)
            room = self.service.state.rooms.get(el.room_id)
            room_name = room.name if room else el.room_id
            self.elements_table.setItem(i, 1, QTableWidgetItem(room_name))
            self.elements_table.setItem(i, 2, QTableWidgetItem(el.category))
            self.elements_table.setItem(i, 3, QTableWidgetItem(el.status))

            fire_btn = QPushButton("TRIGGER")
            if el.requires_confirmation:
                fire_btn.setObjectName("danger")

            def make_fire(element: ShowElement):
                def fire() -> None:
                    if element.requires_confirmation:
                        ok = QMessageBox.question(
                            self,
                            "Critical Cue Confirmation",
                            f"Trigger critical cue '{element.name}'?",
                        )
                        if ok != QMessageBox.Yes:
                            return
                    self.service.trigger_element(element.id)
                    self._element_selected()

                return fire

            fire_btn.clicked.connect(make_fire(el))
            self.elements_table.setCellWidget(i, 4, fire_btn)

        selected_row = -1
        if self.selected_element_id:
            for i, el in enumerate(rows):
                if el.id == self.selected_element_id:
                    selected_row = i
                    break
        if selected_row < 0 and rows:
            selected_row = 0

        self.elements_table.blockSignals(False)
        if selected_row >= 0:
            self.elements_table.selectRow(selected_row)
            self._element_selected()
        else:
            self.selected_element_id = ""
            self.details.clear()

    @staticmethod
    def _wrap(title: str, widget: QWidget) -> QGroupBox:
        box = QGroupBox(title)
        lay = QVBoxLayout(box)
        lay.addWidget(widget)
        return box
