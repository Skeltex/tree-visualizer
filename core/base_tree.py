from __future__ import annotations
import uuid
from enum import Enum
from typing import Optional, Callable, Any, Generator


class EventType(Enum):
    """Типы событий, которые дерево отправляет графическому интерфейсу."""

    INSERT = "INSERT"  # Узел добавлен
    DELETE = "DELETE"  # Узел удален
    ROTATE = "ROTATE"  # Произошел поворот поддерева (балансировка)
    RECOLOR = "RECOLOR"  # Узел изменил цвет (для Красно-черного дерева)
    TRAVERSE = "TRAVERSE"  # Шаг алгоритма (для подсветки пути поиска/обхода)
    FOUND = "FOUND"  # Элемент успешно найден
    NOT_FOUND = "NOT_FOUND"  # Элемент не найден


class Node:
    """
    Базовый класс узла дерева.
    Не содержит логики, только хранит данные и связи.
    """

    def __init__(self, key: int):
        self.key: int = key
        # Уникальный ID позволяет графической сцене не терять узел после балансировок
        self.id: str = str(uuid.uuid4())

        self.left: Optional[Node] = None
        self.right: Optional[Node] = None
        self.parent: Optional[Node] = None

        # Словарь для хранения специфичных данных разных деревьев
        # Например: meta['height'] для AVL, meta['color'] для RB-дерева
        self.meta: dict[str, Any] = {}

    def __repr__(self) -> str:
        return f"Node({self.key})"


class BaseTree:
    """
    Абстрактный базовый класс для всех деревьев.
    Реализует паттерн 'Наблюдатель' (Observer) и общие алгоритмы навигации.
    """

    def __init__(self):
        self.root: Optional[Node] = None
        self._observers: list[Callable] = []

    # --- Механизм событий (Паттерн Observer) ---

    def add_observer(self, callback: Callable) -> None:
        """Подписывает функцию на события дерева (вызывается из GUI)."""
        self._observers.append(callback)

    def emit(self, event_type: EventType, node: Optional[Node], **kwargs) -> None:
        """
        Уведомляет всех подписчиков об изменении в дереве.
        **kwargs используется для передачи дополнительных данных (например, direction="LEFT" при повороте).
        """
        for observer in self._observers:
            observer(event_type, node, **kwargs)

    # --- Вспомогательные методы поиска ---

    def get_min(self, node: Node) -> Node:
        """Находит узел с минимальным значением в заданном поддереве."""
        current = node
        while current.left:
            self.emit(EventType.TRAVERSE, current)
            current = current.left
        self.emit(EventType.TRAVERSE, current)
        return current

    def get_max(self, node: Node) -> Node:
        """Находит узел с максимальным значением в заданном поддереве."""
        current = node
        while current.right:
            self.emit(EventType.TRAVERSE, current)
            current = current.right
        self.emit(EventType.TRAVERSE, current)
        return current

    # --- Навигация ---

    def get_next(self, node: Node) -> Optional[Node]:
        """
        Находит следующий по величине узел (Successor).
        Правило:
        1. Если есть правое поддерево - это минимум в правом поддереве.
        2. Иначе - идем вверх, пока не станем левым потомком своего родителя.
        """
        if node.right:
            return self.get_min(node.right)

        current = node
        parent = node.parent
        while parent and current == parent.right:
            current = parent
            parent = parent.parent

        if parent:
            self.emit(EventType.FOUND, parent)
        else:
            self.emit(EventType.NOT_FOUND, node)

        return parent

    def get_prev(self, node: Node) -> Optional[Node]:
        """
        Находит предыдущий по величине узел (Predecessor).
        Правило:
        1. Если есть левое поддерево - это максимум в левом поддереве.
        2. Иначе - идем вверх, пока не станем правым потомком своего родителя.
        """
        if node.left:
            return self.get_max(node.left)

        current = node
        parent = node.parent
        while parent and current == parent.left:
            current = parent
            parent = parent.parent

        if parent:
            self.emit(EventType.FOUND, parent)
        else:
            self.emit(EventType.NOT_FOUND, node)

        return parent

    # --- Обходы дерева (Traversals) ---
    # Реализованы как генераторы для гибкости, параллельно генерируют события для GUI

    def pre_order(self, node: Optional[Node]) -> Generator[Node, None, None]:
        """Прямой обход (NLR - Node, Left, Right)."""
        if node:
            self.emit(EventType.TRAVERSE, node)
            yield node
            yield from self.pre_order(node.left)
            yield from self.pre_order(node.right)

    def in_order(self, node: Optional[Node]) -> Generator[Node, None, None]:
        """Симметричный обход (LNR - Left, Node, Right). Возвращает элементы по возрастанию."""
        if node:
            yield from self.in_order(node.left)
            self.emit(EventType.TRAVERSE, node)
            yield node
            yield from self.in_order(node.right)

    def post_order(self, node: Optional[Node]) -> Generator[Node, None, None]:
        """Обратный обход (LRN - Left, Right, Node)."""
        if node:
            yield from self.post_order(node.left)
            yield from self.post_order(node.right)
            self.emit(EventType.TRAVERSE, node)
            yield node
