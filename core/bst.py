"""Модуль с реализацией обычного бинарного дерева поиска (BST)."""

from typing import Optional
from core.base_tree import BaseTree, Node, EventType


class BST(BaseTree):
    """Классическое бинарное дерево поиска без балансировки."""

    def insert(self, key: int) -> Optional[Node]:
        """Вставляет ключ и возвращает узел или None при дубликате."""
        if not self.root:
            self.root = Node(key)
            self.emit(EventType.INSERT, self.root)
            return self.root

        current = self.root
        while True:
            self.emit(EventType.TRAVERSE, current)
            if key < current.key:
                if current.left is None:
                    new_node = Node(key)
                    current.left = new_node
                    new_node.parent = current
                    self.emit(EventType.INSERT, new_node)
                    return new_node
                current = current.left
            elif key > current.key:
                if current.right is None:
                    new_node = Node(key)
                    current.right = new_node
                    new_node.parent = current
                    self.emit(EventType.INSERT, new_node)
                    return new_node
                current = current.right
            else:
                return None

    def search(self, key: int) -> Optional[Node]:
        """Ищет узел по ключу и генерирует события поиска."""
        current = self.root
        last_node = None

        while current:
            self.emit(EventType.TRAVERSE, current)
            last_node = current
            if key == current.key:
                self.emit(EventType.FOUND, current)
                return current
            current = current.left if key < current.key else current.right

        self.emit(EventType.NOT_FOUND, last_node)
        return None

    def _transplant(self, u: Node, v: Optional[Node]) -> None:
        """Меняет одно поддерево на другое."""
        if u.parent is None:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v

        if v is not None:
            v.parent = u.parent

    def delete(self, key: int) -> bool:
        """Удаляет узел по ключу и сохраняет структуру дерева."""
        node_to_delete = self.search(key)
        if not node_to_delete:
            return False

        if node_to_delete.left is None:
            self._transplant(node_to_delete, node_to_delete.right)
        elif node_to_delete.right is None:
            self._transplant(node_to_delete, node_to_delete.left)
        else:
            successor = self.get_min(node_to_delete.right)
            if successor.parent != node_to_delete:
                self._transplant(successor, successor.right)
                successor.right = node_to_delete.right
                successor.right.parent = successor
            self._transplant(node_to_delete, successor)
            successor.left = node_to_delete.left
            successor.left.parent = successor

        node_to_delete.parent = node_to_delete.left = node_to_delete.right = None
        self.emit(EventType.DELETE, node_to_delete)
        return True
