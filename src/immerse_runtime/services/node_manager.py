from __future__ import annotations

import random
from datetime import datetime, timezone

from immerse_runtime.models.entities import Node


class NodeManager:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}

    def load(self, project: dict) -> None:
        self.nodes = {
            node["id"]: Node(
                id=node["id"],
                name=node["name"],
                type=node["type"],
                transport=node.get("transport", "mock"),
            )
            for node in project.get("nodes", [])
        }

    def heartbeat(self) -> None:
        for node in self.nodes.values():
            node.last_seen = datetime.now(timezone.utc)
            if random.random() > 0.95:
                node.status = "degraded"
            else:
                node.status = "online"
