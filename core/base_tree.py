"""Общие структуры и алгоритмы для деревьев и событийной визуализации."""

from __future__ import annotations
import uuid
from enum import Enum
from typing import Optional, Callable, Any, Generator


class EventType(Enum):
    """Типы событий, генерируемых моделью для UI/визуализации."""

    INSERT = "INSERT"
    DELETE = "DELETE"
    ROTATE = "ROTATE"
    RECOLOR = "RECOLOR"
    TRAVERSE = "TRAVERSE"
    FOUND = "FOUND"
    NOT_FOUND = "NOT_FOUND"


class Node:
    """Базовая структура узла: ключ, ссылки и вспомогательные метаданные."""

    def __init__(self, key: int):
        self.key: int = key
        self.id: str = str(uuid.uuid4())
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None
        self.parent: Optional[Node] = None
        self.meta: dict[str, Any] = {}

    def __repr__(self) -> str:
        return f"Node({self.key})"


class BaseTree:
    """Базовый класс для деревьев: общие алгоритмы навигации и механизм событий (Observer)."""

    def __init__(self):
        self.root: Optional[Node] = None
        self._observers: list[Callable] = []

    def add_observer(self, callback: Callable) -> None:
        """Добавить подписчика на события модели."""
        self._observers.append(callback)

    def emit(self, event_type: EventType, node: Optional[Node], **kwargs) -> None:
        """Оповестить всех подписчиков о событии модели. Доп. параметры через kwargs."""
        for observer in self._observers:
            observer(event_type, node, **kwargs)

    def get_min(self, node: Node) -> Node:
        """Возвращает минимальный узел в поддереве (левый край)."""
        current = node
        while current.left:
            self.emit(EventType.TRAVERSE, current)
            current = current.left
        self.emit(EventType.TRAVERSE, current)
        return current

    def get_max(self, node: Node) -> Node:
        """Возвращает максимальный узел в поддереве (правый край)."""
        current = node
        while current.right:
            self.emit(EventType.TRAVERSE, current)
            current = current.right
        self.emit(EventType.TRAVERSE, current)
        return current

    def get_next(self, node: Node) -> Optional[Node]:
        """Находит следующий по величине узел (successor)."""
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
        """Находит предыдущий по величине узел (predecessor)."""
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
