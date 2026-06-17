from PySide6.QtWidgets import QGraphicsObject, QGraphicsItem
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont


class NodeItem(QGraphicsObject):
    def __init__(self, node_id: str, key: int, radius: int = 20):
        super().__init__()
        self.node_id = node_id
        self.key = key
        self.radius = radius
        self.border_width = 2

        # РАЗДЕЛЯЕМ ЦВЕТА: Базовый (навсегда) и Текущий (для анимации)
        self.base_bg = QColor("white")
        self.base_border = QColor("black")
        self.base_text = QColor("black")

        self.current_bg = self.base_bg
        self.current_border = self.base_border
        self.current_text = self.base_text

        self.edges = []

        # КРИТИЧЕСКИ ВАЖНО: Разрешаем отслеживать изменение координат (Используем QGraphicsItem)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

    def boundingRect(self) -> QRectF:
        return QRectF(-self.radius, -self.radius, self.radius * 2, self.radius * 2)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Рисуем круг всегда текущим цветом
        pen = QPen(self.current_border, self.border_width)
        painter.setPen(pen)
        painter.setBrush(QBrush(self.current_bg))
        painter.drawEllipse(self.boundingRect())

        painter.setPen(QPen(self.current_text))
        font = QFont("Arial", 11, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(
            self.boundingRect(), Qt.AlignmentFlag.AlignCenter, str(self.key)
        )

    def set_base_color(
        self, bg_color: str, border_color: str = "black", text_color: str = "black"
    ):
        self.base_bg = QColor(bg_color)
        self.base_border = QColor(border_color)
        self.base_text = QColor(text_color)
        self.current_bg = self.base_bg
        self.current_border = self.base_border
        self.current_text = self.base_text
        self.update()

    def set_highlight(
        self, bg_color: str, border_color: str, text_color: str = "black"
    ):
        self.current_bg = QColor(bg_color)
        self.current_border = QColor(border_color)
        self.current_text = QColor(text_color)
        self.update()

    def remove_highlight(self):
        self.current_bg = self.base_bg
        self.current_border = self.base_border
        self.current_text = self.base_text
        self.update()

    def add_edge(self, edge):
        self.edges.append(edge)

    def remove_edge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)

    def itemChange(self, change, value):
        # Если координаты изменились - дергаем все привязанные линии!
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self.edges:
                edge.update_position()
        return super().itemChange(change, value)
