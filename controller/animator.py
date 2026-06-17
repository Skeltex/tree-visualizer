from PySide6.QtCore import (
    QObject,
    QTimer,
    QPropertyAnimation,
    QParallelAnimationGroup,
    QEasingCurve,
    Signal,
)
from core.base_tree import EventType, Node
from typing import Optional, Dict, Any


class TreeLayout:
    """
    Вспомогательный класс для расчета (x, y) координат узлов.
    Использует In-Order обход: X зависит от порядка узла при симметричном обходе,
    Y зависит от глубины узла. Это гарантирует, что узлы никогда не наложатся друг на друга.
    """

    H_SPACING = 50  # Горизонтальное расстояние
    V_SPACING = 70  # Вертикальное расстояние

    @staticmethod
    def calculate(root: Optional[Node]) -> Dict[str, dict]:
        layout = {}
        index = 0

        def traverse(node: Optional[Node], depth: int):
            nonlocal index
            if not node:
                return

            traverse(node.left, depth + 1)

            # ВОТ ЗДЕСЬ КЛЮЧ К РЕБРАМ: parent_id
            layout[node.id] = {
                "x": index * TreeLayout.H_SPACING,
                "y": depth * TreeLayout.V_SPACING,
                "parent_id": node.parent.id if node.parent else None,
            }
            index += 1

            traverse(node.right, depth + 1)

        traverse(root, 0)

        if root and root.id in layout:
            root_x = layout[root.id]["x"]
            for node_id in layout:
                layout[node_id]["x"] -= root_x

        return layout


class Animator(QObject):
    """
    Координатор анимаций. Слушает математическую модель дерева,
    записывает шаги и плавно воспроизводит их на графической сцене.
    """

    # Сигнал, который отправляется в главное окно, когда все анимации завершены
    # (чтобы разблокировать кнопки UI)
    sequence_finished = Signal()

    def __init__(self, scene: Any, tree: Any, speed_ms: int = 500):
        super().__init__()
        self.scene = scene  # Ссылка на QGraphicsScene (напишем позже)
        self.tree = tree  # Экземпляр дерева (BST, AVL, RB, Splay)
        self.speed_ms = speed_ms  # Длительность одной анимации

        self.queue: list[dict] = []  # Очередь кадров
        self.is_playing = False

        # Подписываемся на события дерева
        self.tree.add_observer(self.on_tree_event)

    def on_tree_event(self, event_type: EventType, node: Optional[Node], **kwargs):
        """
        Ловит сигнал от логики дерева. Выполняется мгновенно!
        """
        # Делаем снимок текущего расположения ВСЕХ узлов
        layout_snapshot = TreeLayout.calculate(self.tree.root)

        # Сохраняем примитивы (значения), а не ссылки на объекты,
        # так как объект Node может измениться в следующую микросекунду
        node_info = None
        if node:
            node_info = {
                "id": node.id,
                "key": node.key,
                "meta": dict(node.meta),  # Копируем цвет/высоту на данный момент
            }

        frame = {
            "type": event_type,
            "node": node_info,
            "kwargs": kwargs,
            "layout": layout_snapshot,
        }
        self.queue.append(frame)

    def play(self):
        """Запускает проигрывание очереди, если оно еще не идет."""
        if not self.is_playing and self.queue:
            self.is_playing = True
            self._play_next_frame()

    def _play_next_frame(self):
        """Берет следующий кадр из очереди и анимирует его."""
        if not self.queue:
            self.is_playing = False
            self.sequence_finished.emit()  # Сообщаем GUI, что можно принимать новые команды
            return

        frame = self.queue.pop(0)
        event_type = frame["type"]
        node_info = frame["node"]
        layout = frame["layout"]

        # 1. Обработка логики кадра
        if event_type == EventType.INSERT:
            # Говорим сцене создать новый кружок
            self.scene.add_node_item(node_info)

        elif event_type == EventType.DELETE:
            # Говорим сцене удалить кружок
            self.scene.remove_node_item(node_info["id"])

        elif event_type == EventType.RECOLOR:
            color = frame["kwargs"].get("color", "BLACK")
            self.scene.set_node_color(node_info["id"], color)

        elif event_type == EventType.TRAVERSE:
            self.scene.highlight_node(node_info["id"], "YELLOW")

        elif event_type == EventType.FOUND:
            self.scene.highlight_node(node_info["id"], "GREEN")

        elif event_type == EventType.NOT_FOUND:
            if node_info:
                self.scene.highlight_node(node_info["id"], "RED")

        # 2. Анимация перемещения (самая важная часть)
        # Создаем группу, чтобы все узлы двигались одновременно (параллельно)
        self.anim_group = QParallelAnimationGroup()
        animations_added = False

        for node_id, coords in layout.items():
            item = self.scene.get_node_item(node_id)
            if item:
                # Текущая позиция узла на экране
                start_pos = item.pos()
                # Новая позиция из снапшота
                end_pos = item.scenePos()  # fallback
                end_pos.setX(coords["x"])
                end_pos.setY(coords["y"])

                # Если позиция изменилась (например, произошел ROTATE)
                if start_pos != end_pos or event_type == EventType.INSERT:
                    # Если это новая вставка, узел вылетает из родителя или сверху
                    if event_type == EventType.INSERT and node_id == node_info["id"]:
                        item.setPos(end_pos.x(), end_pos.y() - 50)
                        item.setOpacity(0)

                        # Анимация появления
                        fade_anim = QPropertyAnimation(item, b"opacity")
                        fade_anim.setEndValue(1)
                        fade_anim.setDuration(self.speed_ms)
                        self.anim_group.addAnimation(fade_anim)

                    # Анимация движения
                    move_anim = QPropertyAnimation(item, b"pos")
                    move_anim.setEndValue(end_pos)
                    move_anim.setDuration(self.speed_ms)
                    move_anim.setEasingCurve(
                        QEasingCurve.Type.InOutQuad
                    )  # Плавный старт и торможение
                    self.anim_group.addAnimation(move_anim)
                    animations_added = True

        # Сцена должна перерисовать линии связей во время движения кружков
        self.scene.update_edges_to_target(layout)

        # 3. Запуск анимации или таймера
        if animations_added:
            self.anim_group.finished.connect(self._play_next_frame)
            self.anim_group.start()
        else:
            # Если двигать некого (например, просто подсветили узел при поиске),
            # ждем немного и переходим к следующему кадру
            delay = (
                self.speed_ms
                if event_type
                in (EventType.TRAVERSE, EventType.FOUND, EventType.NOT_FOUND)
                else 50
            )
            QTimer.singleShot(delay, self._play_next_frame)
