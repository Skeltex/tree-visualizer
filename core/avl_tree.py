"""Модуль с реализацией самобалансирующегося AVL-дерева."""

from typing import Optional
from core.base_tree import Node, EventType
from core.bst import BST


class AVLTree(BST):
    """Самобалансирующееся AVL-дерево с подсчетом высот узлов."""

    def _get_height(self, node: Optional[Node]) -> int:
        """Возвращает высоту узла или 0 для пустого узла."""
        if not node:
            return 0
        return node.meta.get("height", 1)

    def _update_height(self, node: Node) -> None:
        """Обновляет метаданные высоты узла."""
        node.meta["height"] = 1 + max(
            self._get_height(node.left), self._get_height(node.right)
        )

    def _get_balance(self, node: Optional[Node]) -> int:
        """Вычисляет баланс узла: высота левого минус правого поддерева."""
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _rotate_right(self, y: Node) -> Node:
        """Выполняет правый поворот и возвращает новый корень поддерева."""
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        x.parent = y.parent
        if y.parent is None:
            self.root = x
        elif y == y.parent.right:
            y.parent.right = x
        else:
            y.parent.left = x
        y.parent = x
        if T2:
            T2.parent = y
        self._update_height(y)
        self._update_height(x)
        self.emit(EventType.ROTATE, y, direction="RIGHT")
        return x

    def _rotate_left(self, x: Node) -> Node:
        """Выполняет левый поворот и возвращает новый корень поддерева."""
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        x.parent = y
        if T2:
            T2.parent = x
        self._update_height(x)
        self._update_height(y)
        self.emit(EventType.ROTATE, x, direction="LEFT")
        return y

    def _balance_node(self, node: Node) -> Node:
        """Балансирует узел и возвращает его новый корень."""
        self._update_height(node)
        balance = self._get_balance(node)
        if balance > 1:
            if self._get_balance(node.left) < 0:
                self._rotate_left(node.left)
            return self._rotate_right(node)
        if balance < -1:
            if self._get_balance(node.right) > 0:
                self._rotate_right(node.right)
            return self._rotate_left(node)
        return node

    def insert(self, key: int) -> Optional[Node]:
        """Вставляет ключ с последующей балансировкой по пути к корню."""
        new_node = super().insert(key)
        if not new_node:
            return None
        new_node.meta["height"] = 1
        curr = new_node.parent
        while curr:
            curr = self._balance_node(curr).parent
        return new_node

    def delete(self, key: int) -> bool:
        """Удаляет ключ и поддерживает баланс дерева."""
        node_to_delete = self.search(key)
        if not node_to_delete:
            return False
        balance_start_node = None
        if node_to_delete.left is None:
            balance_start_node = node_to_delete.parent
            self._transplant(node_to_delete, node_to_delete.right)
        elif node_to_delete.right is None:
            balance_start_node = node_to_delete.parent
            self._transplant(node_to_delete, node_to_delete.left)
        else:
            successor = self.get_min(node_to_delete.right)
            if successor.parent != node_to_delete:
                balance_start_node = successor.parent
                self._transplant(successor, successor.right)
                successor.right = node_to_delete.right
                successor.right.parent = successor
            else:
                balance_start_node = successor
            self._transplant(node_to_delete, successor)
            successor.left = node_to_delete.left
            successor.left.parent = successor
        node_to_delete.parent = node_to_delete.left = node_to_delete.right = None
        self.emit(EventType.DELETE, node_to_delete)
        curr = balance_start_node
        while curr:
            curr = self._balance_node(curr).parent
        return True
