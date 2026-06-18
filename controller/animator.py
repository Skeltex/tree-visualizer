"""Анимация и позиционирование узлов для визуализации дерева."""

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
    """Расчет координат узлов на сцене по симметричному обходу."""

    H_SPACING = 50
    V_SPACING = 70

    @staticmethod
    def calculate(root: Optional[Node]) -> Dict[str, dict]:
        layout = {}
        index = 0

        def traverse(node: Optional[Node], depth: int):
            nonlocal index
            if not node:
                return

            traverse(node.left, depth + 1)
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
    """Собирает события модели и воспроизводит их в графическом интерфейсе."""

    sequence_finished = Signal()

    def __init__(self, scene: Any, tree: Any, speed_ms: int = 500):
        super().__init__()
        self.scene = scene
        self.tree = tree
        self.speed_ms = speed_ms
        self.queue: list[dict] = []
        self.is_playing = False
        self.tree.add_observer(self.on_tree_event)

    def on_tree_event(self, event_type: EventType, node: Optional[Node], **kwargs):
        """Формирует кадр анимации для события модели."""
        layout_snapshot = TreeLayout.calculate(self.tree.root)
        node_info = None
        if node:
            node_info = {
                "id": node.id,
                "key": node.key,
                "meta": dict(node.meta),
            }

        self.queue.append(
            {
                "type": event_type,
                "node": node_info,
                "kwargs": kwargs,
                "layout": layout_snapshot,
            }
        )

    def play(self):
        """Запускает воспроизведение очереди кадров."""
        if not self.is_playing and self.queue:
            self.is_playing = True
            self._play_next_frame()

    def _play_next_frame(self):
        """Выполняет следующий кадр из очереди."""
        if not self.queue:
            self.is_playing = False
            self.sequence_finished.emit()
            return

        frame = self.queue.pop(0)
        event_type = frame["type"]
        node_info = frame["node"]
        layout = frame["layout"]

        if event_type == EventType.INSERT:
            self.scene.add_node_item(node_info)
        elif event_type == EventType.DELETE:
            self.scene.remove_node_item(node_info["id"])
        elif event_type == EventType.RECOLOR:
            color = frame["kwargs"].get("color", "BLACK")
            self.scene.set_node_color(node_info["id"], color)
        elif event_type == EventType.TRAVERSE:
            self.scene.highlight_node(node_info["id"], "YELLOW")
        elif event_type == EventType.FOUND:
            self.scene.highlight_node(node_info["id"], "GREEN")
        elif event_type == EventType.NOT_FOUND and node_info:
            self.scene.highlight_node(node_info["id"], "RED")

        self.anim_group = QParallelAnimationGroup()
        animations_added = False

        for node_id, coords in layout.items():
            item = self.scene.get_node_item(node_id)
            if not item:
                continue

            start_pos = item.pos()
            end_pos = item.scenePos()
            end_pos.setX(coords["x"])
            end_pos.setY(coords["y"])

            if start_pos != end_pos or event_type == EventType.INSERT:
                if event_type == EventType.INSERT and node_id == node_info["id"]:
                    item.setPos(end_pos.x(), end_pos.y() - 50)
                    item.setOpacity(0)
                    fade_anim = QPropertyAnimation(item, b"opacity")
                    fade_anim.setEndValue(1)
                    fade_anim.setDuration(self.speed_ms)
                    self.anim_group.addAnimation(fade_anim)

                move_anim = QPropertyAnimation(item, b"pos")
                move_anim.setEndValue(end_pos)
                move_anim.setDuration(self.speed_ms)
                move_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
                self.anim_group.addAnimation(move_anim)
                animations_added = True

        self.scene.update_edges_to_target(layout)

        if animations_added:
            self.anim_group.finished.connect(self._play_next_frame)
            self.anim_group.start()
        else:
            delay = (
                self.speed_ms
                if event_type
                in (EventType.TRAVERSE, EventType.FOUND, EventType.NOT_FOUND)
                else 50
            )
            QTimer.singleShot(delay, self._play_next_frame)
