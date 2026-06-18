"""Линия, соединяющая два узла на сцене QGraphicsScene."""

from PySide6.QtWidgets import QGraphicsLineItem
from PySide6.QtCore import QLineF
from PySide6.QtGui import QPen, QColor


class EdgeItem(QGraphicsLineItem):
    """Ребро между двумя узлами, обновляющееся при движении узлов."""

    def __init__(self, source_node, dest_node):
        super().__init__()
        self.source_node = source_node
        self.dest_node = dest_node
        self.source_node.add_edge(self)
        self.dest_node.add_edge(self)
        self.setZValue(-1)
        pen = QPen(QColor("gray"), 2)
        self.setPen(pen)
        self.update_position()

    def update_position(self):
        """
        Обновляет начальную и конечную точку линии.
        Вызывается автоматически из NodeItem.itemChange().
        """
        line = QLineF(self.source_node.pos(), self.dest_node.pos())
        self.setLine(line)

    def destroy(self):
        """Безопасное удаление линии (отвязываем от узлов)."""
        self.source_node.remove_edge(self)
        self.dest_node.remove_edge(self)
