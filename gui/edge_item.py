from PySide6.QtWidgets import QGraphicsLineItem
from PySide6.QtCore import QLineF
from PySide6.QtGui import QPen, QColor


class EdgeItem(QGraphicsLineItem):
    """
    Графическое представление связи (линии) между двумя узлами.
    """

    def __init__(self, source_node, dest_node):
        super().__init__()
        self.source_node = source_node
        self.dest_node = dest_node

        # Автоматически привязываем эту линию к обоим узлам
        self.source_node.add_edge(self)
        self.dest_node.add_edge(self)

        # Устанавливаем Z-индекс в -1, чтобы линия рисовалась ПОД кружочками узлов,
        # а не пересекала их текст.
        self.setZValue(-1)

        # Внешний вид линии
        pen = QPen(QColor("gray"), 2)
        self.setPen(pen)

        # Устанавливаем начальные координаты
        self.update_position()

    def update_position(self):
        """
        Обновляет начальную и конечную точку линии.
        Вызывается автоматически из NodeItem.itemChange().
        """
        # Рисуем линию от центра (pos) первого узла до центра второго
        line = QLineF(self.source_node.pos(), self.dest_node.pos())
        self.setLine(line)

    def destroy(self):
        """Безопасное удаление линии (отвязываем от узлов)."""
        self.source_node.remove_edge(self)
        self.dest_node.remove_edge(self)
        # На самой сцене (QGraphicsScene) метод removeItem будет вызван отдельно
