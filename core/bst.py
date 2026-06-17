from typing import Optional
from core.base_tree import BaseTree, Node, EventType


class BST(BaseTree):
    """
    Классическое бинарное дерево поиска (Binary Search Tree).
    Без автоматической балансировки.
    """

    def insert(self, key: int) -> Optional[Node]:
        """Вставка нового элемента в дерево."""
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
                # Дубликаты в нашем дереве игнорируются (можно изменить логику при необходимости)
                return None

    def search(self, key: int) -> Optional[Node]:
        """Поиск элемента по ключу."""
        current = self.root
        while current:
            self.emit(EventType.TRAVERSE, current)
            if key == current.key:
                self.emit(EventType.FOUND, current)
                return current
            elif key < current.key:
                current = current.left
            else:
                current = current.right

        self.emit(EventType.NOT_FOUND, None)
        return None

    def _transplant(self, u: Node, v: Optional[Node]) -> None:
        """
        Вспомогательный метод для удаления.
        Заменяет поддерево с корнем 'u' на поддерево с корнем 'v'.
        """
        if u.parent is None:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v

        if v is not None:
            v.parent = u.parent

    def delete(self, key: int) -> bool:
        """
        Удаление элемента с физическим перестроением связей (Pointer Rewiring).
        Возвращает True, если элемент был удален, и False, если не найден.
        """
        # Сначала ищем узел (search сам сгенерирует события TRAVERSE для визуализации)
        node_to_delete = self.search(key)
        if not node_to_delete:
            return False

        # Случай 1: Нет левого потомка (или вообще нет потомков)
        if node_to_delete.left is None:
            self._transplant(node_to_delete, node_to_delete.right)

        # Случай 2: Нет правого потомка
        elif node_to_delete.right is None:
            self._transplant(node_to_delete, node_to_delete.left)

        # Случай 3: Есть оба потомка
        else:
            # Ищем преемника (минимальный элемент в правом поддереве)
            # get_min также сгенерирует TRAVERSE, так что пользователь увидит этот поиск
            successor = self.get_min(node_to_delete.right)

            # Если преемник не является прямым потомком удаляемого узла
            if successor.parent != node_to_delete:
                self._transplant(successor, successor.right)
                successor.right = node_to_delete.right
                successor.right.parent = successor

            # Заменяем удаляемый узел преемником
            self._transplant(node_to_delete, successor)
            successor.left = node_to_delete.left
            successor.left.parent = successor

        # Очищаем связи удаленного узла для сборщика мусора и сообщаем GUI
        node_to_delete.parent = node_to_delete.left = node_to_delete.right = None
        self.emit(EventType.DELETE, node_to_delete)

        return True
