"""Simple generic node graph scene used by puzzle and logic editors."""
from __future__ import annotations

import uuid

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsItem, QGraphicsRectItem, QGraphicsScene, QGraphicsSimpleTextItem

from escape_room_designer.models.project_model import GraphEdge, GraphNode


class GraphNodeItem(QGraphicsRectItem):
    def __init__(self, node: GraphNode, color: str = "#314862"):
        super().__init__(0, 0, 180, 72)
        self.node = node
        self.setPos(node.x, node.y)
        self.setBrush(QBrush(QColor(color)))
        self.setPen(QPen(QColor("#92b2d9"), 1.2))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        title = QGraphicsSimpleTextItem(node.label, self)
        title.setPos(8, 8)
        title.setBrush(QColor("#e8f1ff"))
        self.in_pin = QGraphicsEllipseItem(-8, 28, 12, 12, self)
        self.in_pin.setBrush(QBrush(QColor("#81d4fa")))
        self.out_pin = QGraphicsEllipseItem(176, 28, 12, 12, self)
        self.out_pin.setBrush(QBrush(QColor("#ffcc80")))

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.node.x = float(value.x())
            self.node.y = float(value.y())
        return super().itemChange(change, value)


class NodeScene(QGraphicsScene):
    def __init__(self):
        super().__init__(-2500, -2500, 5000, 5000)
        self._edges: list[GraphEdge] = []

    def add_node(self, node_type: str, label: str, x: float = 0, y: float = 0) -> GraphNodeItem:
        node = GraphNode(node_id=str(uuid.uuid4()), node_type=node_type, label=label, x=x, y=y)
        item = GraphNodeItem(node)
        self.addItem(item)
        return item

    def connect_selected(self) -> None:
        selected = [item for item in self.selectedItems() if isinstance(item, GraphNodeItem)]
        if len(selected) != 2:
            return
        src, dst = selected
        self._edges.append(GraphEdge(source=src.node.node_id, target=dst.node.node_id))
        self.addLine(
            src.scenePos().x() + 180,
            src.scenePos().y() + 36,
            dst.scenePos().x(),
            dst.scenePos().y() + 36,
            QPen(QColor("#5f89bd"), 2),
        )

    def export_graph(self) -> tuple[list[GraphNode], list[GraphEdge]]:
        nodes: list[GraphNode] = []
        for item in self.items():
            if isinstance(item, GraphNodeItem):
                nodes.append(item.node)
        return nodes, self._edges

    def import_graph(self, nodes: list[GraphNode], edges: list[GraphEdge]) -> None:
        self.clear()
        self._edges = list(edges)
        node_items: dict[str, GraphNodeItem] = {}
        for node in nodes:
            item = GraphNodeItem(node)
            self.addItem(item)
            node_items[node.node_id] = item
        for edge in self._edges:
            src = node_items.get(edge.source)
            dst = node_items.get(edge.target)
            if src and dst:
                self.addLine(
                    src.scenePos().x() + 180,
                    src.scenePos().y() + 36,
                    dst.scenePos().x(),
                    dst.scenePos().y() + 36,
                    QPen(QColor("#5f89bd"), 2),
                )

    def drawBackground(self, painter, rect: QRectF):
        super().drawBackground(painter, rect)
        painter.setPen(QPen(QColor("#1a2230"), 1))
        step = 30
        x = int(rect.left()) - (int(rect.left()) % step)
        while x < rect.right():
            painter.drawLine(x, rect.top(), x, rect.bottom())
            x += step
        y = int(rect.top()) - (int(rect.top()) % step)
        while y < rect.bottom():
            painter.drawLine(rect.left(), y, rect.right(), y)
            y += step
