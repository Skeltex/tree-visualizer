from typing import Optional
from core.base_tree import Node, EventType
from core.bst import BST


class AVLTree(BST):
    """
    Самобалансирующееся AVL-дерево.
    Гарантирует высоту O(log N) за счет малых и больших вращений.
    """

    # --- Вспомогательные методы для работы с высотой ---

    def _get_height(self, node: Optional[Node]) -> int:
        """Безопасное получение высоты узла (пустой узел имеет высоту 0)."""
        if not node:
            return 0
        return node.meta.get("height", 1)

    def _update_height(self, node: Node) -> None:
        """Пересчет высоты узла на основе его потомков."""
        node.meta["height"] = 1 + max(
            self._get_height(node.left), self._get_height(node.right)
        )

    def _get_balance(self, node: Optional[Node]) -> int:
        """
        Вычисление фактора баланса (Balance Factor).
        > 1  : Перевес в левую сторону
        < -1 : Перевес в правую сторону
        """
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    # --- Механика вращений (Ротации) ---

    def _rotate_right(self, y: Node) -> Node:
        """
        Правый поворот вокруг узла y.
        Возвращает новый корень поддерева.
        """
        x = y.left
        T2 = x.right

        # Перестраиваем связи
        x.right = y
        y.left = T2

        # Обновляем родителей
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

        # Обновляем высоты (важен порядок: сначала y (он теперь ниже), затем x)
        self._update_height(y)
        self._update_height(x)

        # Сообщаем GUI, что произошел поворот!
        self.emit(EventType.ROTATE, y, direction="RIGHT")

        return x

    def _rotate_left(self, x: Node) -> Node:
        """
        Левый поворот вокруг узла x.
        Возвращает новый корень поддерева.
        """
        y = x.right
        T2 = y.left

        # Перестраиваем связи
        y.left = x
        x.right = T2

        # Обновляем родителей
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

        # Обновляем высоты (сначала x, затем y)
        self._update_height(x)
        self._update_height(y)

        # Сообщаем GUI
        self.emit(EventType.ROTATE, x, direction="LEFT")

        return y

    def _balance_node(self, node: Node) -> Node:
        """
        Проверяет баланс узла и выполняет необходимые повороты.
        Возвращает новый корень этого поддерева.
        """
        self._update_height(node)
        balance = self._get_balance(node)

        # Случай 1: Left Heavy (Перевес слева)
        if balance > 1:
            # Левый-Правый (Left-Right Case) -> нужен двойной поворот
            if self._get_balance(node.left) < 0:
                self._rotate_left(node.left)
            # Левый-Левый (Left-Left Case)
            return self._rotate_right(node)

        # Случай 2: Right Heavy (Перевес справа)
        elif balance < -1:
            # Правый-Левый (Right-Left Case) -> нужен двойной поворот
            if self._get_balance(node.right) > 0:
                self._rotate_right(node.right)
            # Правый-Правый (Right-Right Case)
            return self._rotate_left(node)

        # Узел сбалансирован
        return node

    # --- Публичные методы ---

    def insert(self, key: int) -> Optional[Node]:
        """
        Вставка элемента с последующей балансировкой снизу вверх.
        """
        # Используем логику обычного BST для физической вставки
        new_node = super().insert(key)
        if not new_node:
            return None  # Игнорируем дубликаты

        new_node.meta["height"] = 1

        # Поднимаемся вверх к корню и балансируем дерево
        curr = new_node.parent
        while curr:
            curr = self._balance_node(curr).parent

        return new_node

    def delete(self, key: int) -> bool:
        """
        Удаление элемента с последующей балансировкой снизу вверх.
        """
        node_to_delete = self.search(key)
        if not node_to_delete:
            return False

        # Запоминаем узел, с которого нужно начать балансировку после удаления
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
                # Если преемник - прямой ребенок, балансировку начинаем с него
                balance_start_node = successor

            self._transplant(node_to_delete, successor)
            successor.left = node_to_delete.left
            successor.left.parent = successor

        node_to_delete.parent = node_to_delete.left = node_to_delete.right = None
        self.emit(EventType.DELETE, node_to_delete)

        # Балансируем дерево от места удаления до корня
        curr = balance_start_node
        while curr:
            curr = self._balance_node(curr).parent

        return True
