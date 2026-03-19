from __future__ import annotations

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget


class NodeSimulatorPage(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self.window = window
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Node ID", "Type", "Connected", "Heartbeat", "Last Message", "Latency", "Fault"])
        layout.addWidget(self.table)

    def refresh(self) -> None:
        nodes = list(self.window.engine.nodes.nodes.values())
        self.table.setRowCount(len(nodes))
        for row, node in enumerate(nodes):
            values = [node.node_id, node.node_type, str(node.connected), node.heartbeat, node.last_message, f"{node.latency_ms}ms", node.fault_status]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))
