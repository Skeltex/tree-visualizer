"""Модуль с реализацией Splay-дерева с операцией подъема узла в корень."""

from typing import Optional
from core.base_tree import Node, EventType
from core.bst import BST


class SplayTree(BST):
    """
    Splay-дерево (Косое дерево).
    Самобалансирующееся дерево без хранения дополнительных метаданных.
    При любом обращении к узлу он перемещается в корень дерева (операция Splay).
    """

    def _rotate_left(self, x: Node) -> None:
        """Левый поворот вокруг узла x."""
        y = x.right
        if not y:
            return

        x.right = y.left
        if y.left:
            y.left.parent = x

        y.parent = x.parent
        if not x.parent:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y

        y.left = x
        x.parent = y

        self.emit(EventType.ROTATE, x, direction="LEFT")

    def _rotate_right(self, x: Node) -> None:
        """Правый поворот вокруг узла x."""
        y = x.left
        if not y:
            return

        x.left = y.right
        if y.right:
            y.right.parent = x

        y.parent = x.parent
        if not x.parent:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y

        y.right = x
        x.parent = y

        self.emit(EventType.ROTATE, x, direction="RIGHT")

    def _splay(self, x: Node) -> None:
        """
        Перемещает заданный узел x в корень дерева путем серии ротаций.
        Генерирует цепочку событий ROTATE для графической сцены.
        """
        while x.parent:
            if not x.parent.parent:
                if x == x.parent.left:
                    self._rotate_right(x.parent)
                else:
                    self._rotate_left(x.parent)
            elif x == x.parent.left and x.parent == x.parent.parent.left:
                self._rotate_right(x.parent.parent)
                self._rotate_right(x.parent)
            elif x == x.parent.right and x.parent == x.parent.parent.right:
                self._rotate_left(x.parent.parent)
                self._rotate_left(x.parent)
            elif x == x.parent.right and x.parent == x.parent.parent.left:
                self._rotate_left(x.parent)
                self._rotate_right(x.parent)
            else:
                self._rotate_right(x.parent)
                self._rotate_left(x.parent)

    def search(self, key: int) -> Optional[Node]:
        """
        Поиск с последующим Splay.
        Если элемент не найден, в корень поднимается последний просмотренный узел.
        """
        current = self.root
        last_accessed = None

        while current:
            self.emit(EventType.TRAVERSE, current)
            last_accessed = current

            if key == current.key:
                self.emit(EventType.FOUND, current)
                self._splay(current)
                return current
            elif key < current.key:
                current = current.left
            else:
                current = current.right

        self.emit(EventType.NOT_FOUND, last_accessed)
        if last_accessed:
            self._splay(last_accessed)

        return None

    def insert(self, key: int) -> Optional[Node]:
        """
        Вставка элемента (как в обычном BST) с последующим поднятием его в корень.
        """
        new_node = super().insert(key)

        if new_node:
            self._splay(new_node)

        return new_node

    def delete(self, key: int) -> bool:
        """
        Удаление в Splay-дереве работает изящно:
        1. Поднимаем удаляемый узел в корень (через search).
        2. Удаляем корень, дерево распадается на Левое и Правое.
        3. Находим максимум в Левом поддереве и поднимаем его в корень Левого поддерева.
        4. Прикрепляем Правое поддерево к новому корню.
        """
        node_to_delete = self.search(key)
        if not node_to_delete:
            return False

        left_tree = node_to_delete.left
        right_tree = node_to_delete.right

        if left_tree:
            left_tree.parent = None
        if right_tree:
            right_tree.parent = None
        node_to_delete.left = node_to_delete.right = None

        if not left_tree:
            self.root = right_tree
        else:
            self.root = left_tree
            max_node = self.get_max(left_tree)
            self._splay(max_node)
            max_node.right = right_tree
            if right_tree:
                right_tree.parent = max_node

        self.emit(EventType.DELETE, node_to_delete)

        return True
