"""Сцена для визуализации элементов узлов дерева и их связей."""

from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtGui import QBrush, QColor
from PySide6.QtCore import Signal
from gui.node_item import NodeItem
from gui.edge_item import EdgeItem


class TreeScene(QGraphicsScene):
    """Управляет узлами, ребрами и их визуальным состоянием."""

    node_delete_requested = Signal(int)

    def __init__(self):
        """Инициализирует сцену с параметрами размера и цвета фона."""
        super().__init__()
        self.nodes: dict[str, NodeItem] = {}
        self.setSceneRect(-50000, -50000, 100000, 100000)
        self.setBackgroundBrush(QBrush(QColor("#1e1e2e")))

    def add_node_item(self, node_info: dict) -> NodeItem:
        """Создает и добавляет визуальный узел на сцену с указанными свойствами."""
        node_id = node_info["id"]
        key = node_info["key"]
        item = NodeItem(node_id, key)

        item.right_clicked.connect(self.node_delete_requested.emit)

        self.addItem(item)
        self.nodes[node_id] = item

        color = node_info.get("meta", {}).get("color", "white")
        if color == "RED":
            item.set_base_color("red", "darkred", "white")
        elif color == "BLACK":
            item.set_base_color("#333333", "black", "white")

        return item

    def get_node_item(self, node_id: str) -> NodeItem | None:
        """Возвращает визуальный объект узла по его идентификатору."""
        return self.nodes.get(node_id)

    def remove_node_item(self, node_id: str):
        """Удаляет узел и все привязанные к нему ребра со сцены."""
        item = self.nodes.get(node_id)
        if not item:
            return

        edges_to_remove = list(item.edges)
        for edge in edges_to_remove:
            edge.destroy()
            self.removeItem(edge)

        self.removeItem(item)
        del self.nodes[node_id]

    def set_node_color(self, node_id: str, color_str: str):
        """Устанавливает базовый цвет узла в зависимости от типа (RED, BLACK, другой)."""
        item = self.get_node_item(node_id)
        if not item:
            return

        if color_str == "RED":
            item.set_base_color("red", "darkred", "white")
        elif color_str == "BLACK":
            item.set_base_color("#333333", "black", "white")
        else:
            item.set_base_color(color_str)

    def highlight_node(self, node_id: str, color: str):
        """Подсвечивает узел временным цветом."""
        item = self.get_node_item(node_id)
        if not item:
            return

        if color == "YELLOW":
            item.set_highlight("yellow", "orange", duration_ms=400)
        elif color == "GREEN":
            item.set_highlight("lightgreen", "darkgreen", duration_ms=1500)
        elif color == "RED":
            item.set_highlight("lightcoral", "darkred", duration_ms=1500)

    def _add_edge_if_not_exists(self, parent_id: str, child_id: str):
        """Создает ребро между двумя узлами, если оно еще не существует."""
        parent_item = self.get_node_item(parent_id)
        child_item = self.get_node_item(child_id)
        if not parent_item or not child_item:
            return

        for edge in parent_item.edges:
            if edge.dest_node == child_item or edge.source_node == child_item:
                return

        edge = EdgeItem(parent_item, child_item)
        self.addItem(edge)

    def update_edges_to_target(self, layout: dict):
        """Перестраивает все ребра на основе parent_id из layout."""
        edges_to_remove = [item for item in self.items() if isinstance(item, EdgeItem)]
        for edge in edges_to_remove:
            edge.destroy()
            self.removeItem(edge)

        for node_id, data in layout.items():
            parent_id = data.get("parent_id")
            if parent_id:
                self._add_edge_if_not_exists(parent_id, node_id)

    def clear_scene(self):
        """Очищает сцену и сбрасывает список узлов."""
        self.clear()
        self.nodes.clear()
