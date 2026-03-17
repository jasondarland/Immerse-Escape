"""Device registry and runtime mapping page."""
from __future__ import annotations

import uuid
from typing import Callable

from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from escape_room_designer.models.project_model import Device


class DevicesPage(QWidget):
    def __init__(self):
        super().__init__()
        self._inspector_callback: Callable[[dict[str, str]], None] | None = None

        root = QHBoxLayout(self)
        left = QVBoxLayout()
        right = QVBoxLayout()

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Runtime ID", "Name", "Type", "Room", "Address", "Node"])
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        left.addWidget(self.table)

        form = QFormLayout()
        self.name = QLineEdit()
        self.dtype = QLineEdit("button")
        self.room = QLineEdit("room-1")
        self.address = QLineEdit("GPIO:1")
        self.node = QLineEdit("Node-GPIO")
        self.io_map = QLineEdit("in:1")

        form.addRow("Name", self.name)
        form.addRow("Type", self.dtype)
        form.addRow("Room", self.room)
        form.addRow("Address", self.address)
        form.addRow("Node", self.node)
        form.addRow("I/O Mapping", self.io_map)

        add_btn = QPushButton("Add Device")
        add_btn.clicked.connect(self.add_device)
        del_btn = QPushButton("Remove Selected")
        del_btn.clicked.connect(self.remove_selected)

        right.addLayout(form)
        right.addWidget(add_btn)
        right.addWidget(del_btn)
        right.addStretch()

        root.addLayout(left, 2)
        root.addLayout(right, 1)

    def set_inspector_callback(self, callback: Callable[[dict[str, str]], None]) -> None:
        self._inspector_callback = callback

    def _on_selection_changed(self) -> None:
        if not self._inspector_callback:
            return
        row = self.table.currentRow()
        if row < 0:
            self._inspector_callback({})
            return
        payload = {
            "runtime_id": self.table.item(row, 0).text(),
            "name": self.table.item(row, 1).text(),
            "type": self.table.item(row, 2).text(),
            "room": self.table.item(row, 3).text(),
            "address": self.table.item(row, 4).text(),
            "node": self.table.item(row, 5).text(),
        }
        self._inspector_callback(payload)

    def add_device(self) -> None:
        runtime_id = f"dev-{uuid.uuid4().hex[:8]}"
        row = self.table.rowCount()
        self.table.insertRow(row)
        values = [runtime_id, self.name.text() or "Device", self.dtype.text(), self.room.text(), self.address.text(), self.node.text()]
        for col, value in enumerate(values):
            self.table.setItem(row, col, QTableWidgetItem(value))

    def remove_selected(self) -> None:
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)

    def export_devices(self) -> list[Device]:
        devices = []
        for row in range(self.table.rowCount()):
            devices.append(
                Device(
                    runtime_id=self.table.item(row, 0).text(),
                    name=self.table.item(row, 1).text(),
                    device_type=self.table.item(row, 2).text(),
                    room_id=self.table.item(row, 3).text(),
                    address=self.table.item(row, 4).text(),
                    node_assignment=self.table.item(row, 5).text(),
                    io_mapping=self.io_map.text(),
                    state="online",
                )
            )
        return devices

    def import_devices(self, devices: list[Device]) -> None:
        self.table.setRowCount(0)
        for device in devices:
            row = self.table.rowCount()
            self.table.insertRow(row)
            values = [device.runtime_id, device.name, device.device_type, device.room_id, device.address, device.node_assignment]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))
