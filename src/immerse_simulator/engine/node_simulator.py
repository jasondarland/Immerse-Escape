from __future__ import annotations

from dataclasses import dataclass, field

from immerse_simulator.models.package import Device


@dataclass(slots=True)
class SimNode:
    node_id: str
    node_type: str
    devices: list[Device] = field(default_factory=list)
    connected: bool = True
    heartbeat: str = "healthy"
    last_message: str = "Ready"
    latency_ms: int = 50
    fault_status: str = "none"


class NodeSimulatorManager:
    def __init__(self) -> None:
        self.nodes: dict[str, SimNode] = {}

    def load_devices(self, devices: list[Device]) -> None:
        self.nodes.clear()
        for device in devices:
            node_id = f"{device.node_type.lower()}-{device.room.lower().replace(' ', '-') }"
            node = self.nodes.setdefault(node_id, SimNode(node_id=node_id, node_type=device.node_type))
            node.devices.append(device)

    def set_node_online(self, node_id: str, online: bool) -> None:
        node = self.nodes[node_id]
        node.connected = online
        node.last_message = "Connected" if online else "Disconnected"

    def inject_fault(self, node_id: str, status: str) -> None:
        node = self.nodes[node_id]
        node.fault_status = status
        node.last_message = f"Fault injected: {status}"

    def heartbeat_tick(self) -> None:
        for node in self.nodes.values():
            node.heartbeat = "healthy" if node.connected else "missing"
