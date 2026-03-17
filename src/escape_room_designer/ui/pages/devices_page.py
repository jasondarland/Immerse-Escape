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

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Type", "Subtype", "Room", "Node", "Protocol", "Address"])
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        left.addWidget(self.table)

        form = QFormLayout()
        self.name = QLineEdit()
        self.dtype = QLineEdit("button")
        self.subtype = QLineEdit("generic")
        self.room = QLineEdit("room-1")
        self.node = QLineEdit("node-gpio-1")
        self.protocol = QLineEdit("gpio")
        self.address = QLineEdit("GPIO:1")
        self.zone = QLineEdit("default")

        form.addRow("Name", self.name)
        form.addRow("Type", self.dtype)
        form.addRow("Subtype", self.subtype)
        form.addRow("Room", self.room)
        form.addRow("Zone", self.zone)
        form.addRow("Node", self.node)
        form.addRow("Protocol", self.protocol)
        form.addRow("Address", self.address)

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
        payload = {self.table.horizontalHeaderItem(c).text().lower(): self.table.item(row, c).text() for c in range(self.table.columnCount())}
        self._inspector_callback(payload)

    def add_device(self) -> None:
        device_id = f"dev-{uuid.uuid4().hex[:8]}"
        row = self.table.rowCount()
        self.table.insertRow(row)
        values = [
            device_id,
            self.name.text() or "Device",
            self.dtype.text(),
            self.subtype.text(),
            self.room.text(),
            self.node.text(),
            self.protocol.text(),
            self.address.text(),
        ]
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
                    id=self.table.item(row, 0).text(),
                    name=self.table.item(row, 1).text(),
                    type=self.table.item(row, 2).text(),
                    subtype=self.table.item(row, 3).text(),
                    room_id=self.table.item(row, 4).text(),
                    node_id=self.table.item(row, 5).text(),
                    protocol=self.table.item(row, 6).text(),
                    address=self.table.item(row, 7).text(),
                    zone_id=self.zone.text() or "default",
                    capabilities=["trigger", "state"],
                    default_state="idle",
                    fail_state="safe",
                    tags=[],
                    notes="",
                    simulated_properties={"simulated": True},
                )
            )
        return devices

    def import_devices(self, devices: list[Device]) -> None:
        self.table.setRowCount(0)
        for device in devices:
            row = self.table.rowCount()
            self.table.insertRow(row)
            values = [device.id, device.name, device.type, device.subtype, device.room_id, device.node_id, device.protocol, device.address]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))
