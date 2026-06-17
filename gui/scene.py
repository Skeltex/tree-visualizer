from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtCore import QTimer
from PySide6.QtGui import QBrush, QColor
from gui.node_item import NodeItem
from gui.edge_item import EdgeItem


class TreeScene(QGraphicsScene):
    """
    Интерактивный холст (Сцена) для отрисовки дерева.
    Управляет всеми NodeItem и EdgeItem.
    """

    def __init__(self):
        super().__init__()
        # Словарь для быстрого доступа к узлам по их ID (uuid из логики)
        self.nodes: dict[str, NodeItem] = {}

        # Настраиваем размер сцены. Она может расширяться автоматически,
        # но мы зададим базовый квадрат для центрирования.
        self.setSceneRect(-1000, -1000, 2000, 2000)
        self.setBackgroundBrush(QBrush(QColor("#1e1e2e")))

    # --- Управление Узлами (Nodes) ---

    def add_node_item(self, node_info: dict) -> NodeItem:
        node_id = node_info["id"]
        key = node_info["key"]

        item = NodeItem(node_id, key)
        self.addItem(item)
        self.nodes[node_id] = item

        # Используем новый метод set_base_color
        color = node_info.get("meta", {}).get("color", "white")
        if color == "RED":
            item.set_base_color("red", "darkred", "white")
        elif color == "BLACK":
            item.set_base_color("#333333", "black", "white")

        return item

    def get_node_item(self, node_id: str) -> NodeItem | None:
        """Возвращает графический объект узла по его ID."""
        return self.nodes.get(node_id)

    def remove_node_item(self, node_id: str):
        """Удаляет узел и все связанные с ним линии со сцены."""
        item = self.nodes.get(node_id)
        if item:
            # Важно: сначала удаляем линии, привязанные к этому узлу!
            # Иначе они будут ссылаться на несуществующий объект (C++ краш)
            edges_to_remove = list(item.edges)
            for edge in edges_to_remove:
                edge.destroy()
                self.removeItem(edge)

            self.removeItem(item)
            del self.nodes[node_id]

    def set_node_color(self, node_id: str, color_str: str):
        item = self.get_node_item(node_id)
        if item:
            if color_str == "RED":
                item.set_base_color("red", "darkred", "white")
            elif color_str == "BLACK":
                item.set_base_color("#333333", "black", "white")
            else:
                item.set_base_color(color_str)

    def highlight_node(self, node_id: str, color: str):
        item = self.get_node_item(node_id)
        if not item:
            return

        # Используем подсветку, которая не ломает базовый цвет
        if color == "YELLOW":
            item.set_highlight("yellow", "orange")
        elif color == "GREEN":
            item.set_highlight("lightgreen", "darkgreen")
        elif color == "RED":
            item.set_highlight("lightcoral", "darkred")

        # Через 400мс просто командуем "сбрось подсветку"
        def restore_color():
            if item in self.nodes.values():
                item.remove_highlight()

        QTimer.singleShot(400, restore_color)

    # --- Управление Связями (Edges) ---

    def _add_edge_if_not_exists(self, parent_id: str, child_id: str):
        """Создает линию между двумя узлами, если её еще нет."""
        parent_item = self.get_node_item(parent_id)
        child_item = self.get_node_item(child_id)

        if not parent_item or not child_item:
            return

        # Проверяем, нет ли уже линии между этими двумя узлами
        for edge in parent_item.edges:
            if edge.dest_node == child_item or edge.source_node == child_item:
                return  # Линия уже существует

        edge = EdgeItem(parent_item, child_item)
        self.addItem(edge)

    def update_edges_to_target(self, layout: dict):
        """
        Вызывается Контроллером перед началом анимации.
        Здесь мы должны удалить старые неправильные связи (которые разорвались
        во время ротации) и создать новые правильные связи на основе актуальной логики.

        В этом проекте проще всего удалить ВСЕ линии и перерисовать их заново
        (поскольку узлы знают свои новые логические связи). Но у нас нет прямых
        ссылок на parent/left/right в layout.

        Поэтому мы сделаем хитрее: Контроллер должен передавать нам в layout
        информацию о родителях!
        """
        # Сначала собираем ВСЕ линии на сцене и удаляем их
        # Это кажется затратным, но для 50-100 узлов это микросекунды
        edges_to_remove = []
        for item in self.items():
            if isinstance(item, EdgeItem):
                edges_to_remove.append(item)

        for edge in edges_to_remove:
            edge.destroy()
            self.removeItem(edge)

        # Теперь строим новые линии на основе layout
        for node_id, data in layout.items():
            parent_id = data.get("parent_id")
            if parent_id:
                self._add_edge_if_not_exists(parent_id, node_id)

    def clear_scene(self):
        """Полная очистка холста."""
        self.clear()
        self.nodes.clear()
