from typing import Optional
from core.base_tree import Node, EventType
from core.bst import BST


class RBTree(BST):
    """
    Красно-чёрное дерево.
    Обеспечивает балансировку через перекрашивание узлов и ротации.
    """

    # --- Вспомогательные методы работы с цветом ---

    def _get_color(self, node: Optional[Node]) -> str:
        """Пустые узлы (None) концептуально считаются ЧЕРНЫМИ."""
        if not node:
            return "BLACK"
        return node.meta.get("color", "BLACK")

    def _set_color(self, node: Optional[Node], color: str) -> None:
        """Устанавливает цвет и уведомляет GUI (если узел не фантомный)."""
        if node and not node.meta.get("fake", False):
            node.meta["color"] = color
            self.emit(EventType.RECOLOR, node, color=color)
        elif node and node.meta.get("fake", False):
            node.meta["color"] = color  # Фантомные узлы красим в тишине

    # --- Ротации (без учета высоты, в отличие от AVL) ---

    def _rotate_left(self, x: Node) -> None:
        y = x.right
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

    def _rotate_right(self, y: Node) -> None:
        x = y.left
        y.left = x.right
        if x.right:
            x.right.parent = y

        x.parent = y.parent
        if not y.parent:
            self.root = x
        elif y == y.parent.right:
            y.parent.right = x
        else:
            y.parent.left = x

        x.right = y
        y.parent = x
        self.emit(EventType.ROTATE, y, direction="RIGHT")

    # --- Вставка и её балансировка ---

    def insert(self, key: int) -> Optional[Node]:
        # Физически вставляем как в обычном BST
        new_node = super().insert(key)
        if not new_node:
            return None  # Игнорируем дубликаты

        # Новый узел всегда красный
        self._set_color(new_node, "RED")
        self._insert_fixup(new_node)
        return new_node

    def _insert_fixup(self, z: Node) -> None:
        """Восстановление свойств после вставки."""
        while z.parent and self._get_color(z.parent) == "RED":
            # Parent is left child
            if z.parent == z.parent.parent.left:
                y = z.parent.parent.right  # Uncle
                if self._get_color(y) == "RED":
                    # Случай 1: Дядя красный. Перекрашиваем родителя, дядю и деда.
                    self._set_color(z.parent, "BLACK")
                    self._set_color(y, "BLACK")
                    self._set_color(z.parent.parent, "RED")
                    z = z.parent.parent
                else:
                    if z == z.parent.right:
                        # Случай 2: Дядя черный, узел - правый потомок (зигзаг)
                        z = z.parent
                        self._rotate_left(z)
                    # Случай 3: Дядя черный, узел - левый потомок
                    self._set_color(z.parent, "BLACK")
                    self._set_color(z.parent.parent, "RED")
                    self._rotate_right(z.parent.parent)
            # Parent is right child (симметрично)
            else:
                y = z.parent.parent.left  # Uncle
                if self._get_color(y) == "RED":
                    self._set_color(z.parent, "BLACK")
                    self._set_color(y, "BLACK")
                    self._set_color(z.parent.parent, "RED")
                    z = z.parent.parent
                else:
                    if z == z.parent.left:
                        z = z.parent
                        self._rotate_right(z)
                    self._set_color(z.parent, "BLACK")
                    self._set_color(z.parent.parent, "RED")
                    self._rotate_left(z.parent.parent)

        self._set_color(self.root, "BLACK")

    # --- Удаление и его балансировка ---

    def delete(self, key: int) -> bool:
        z = self.search(key)
        if not z:
            return False

        y = z
        y_original_color = self._get_color(y)

        # x_fake - фантомный узел, если x окажется None
        x_fake = None

        if z.left is None:
            x = z.right
            if x is None:
                x = x_fake = self._create_fake_node(z, is_left=False)
            self._transplant(z, x)
        elif z.right is None:
            x = z.left
            if x is None:
                x = x_fake = self._create_fake_node(z, is_left=True)
            self._transplant(z, x)
        else:
            y = self.get_min(z.right)
            y_original_color = self._get_color(y)
            x = y.right

            if y.parent == z:
                if x is None:
                    x = x_fake = self._create_fake_node(y, is_left=False)
            else:
                if x is None:
                    x = x_fake = self._create_fake_node(y, is_left=False)
                self._transplant(y, x)
                y.right = z.right
                y.right.parent = y

            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
            self._set_color(y, self._get_color(z))  # Наследник забирает цвет удаленного

        z.parent = z.left = z.right = None
        self.emit(EventType.DELETE, z)

        if y_original_color == "BLACK":
            self._delete_fixup(x)

        # Удаляем фантомный узел, если он был создан
        if x_fake:
            self._remove_fake_node(x_fake)

        return True

    def _create_fake_node(self, parent_target: Node, is_left: bool) -> Node:
        """Создает невидимый узел для удержания структуры дерева при удалении черного листа."""
        fake = Node(0)
        fake.meta["color"] = "BLACK"
        fake.meta["fake"] = True
        fake.parent = parent_target
        if is_left:
            parent_target.left = fake
        else:
            parent_target.right = fake
        return fake

    def _remove_fake_node(self, fake: Node) -> None:
        """Тихо убирает фантомный узел после балансировки."""
        if fake.parent:
            if fake == fake.parent.left:
                fake.parent.left = None
            else:
                fake.parent.right = None
        if self.root == fake:
            self.root = None

    def _delete_fixup(self, x: Node) -> None:
        """Восстановление свойств после удаления черного узла (Двойной Черный)."""
        while x != self.root and self._get_color(x) == "BLACK":
            if x == x.parent.left:
                w = x.parent.right  # Sibling (брат)
                if self._get_color(w) == "RED":
                    self._set_color(w, "BLACK")
                    self._set_color(x.parent, "RED")
                    self._rotate_left(x.parent)
                    w = x.parent.right

                if (
                    self._get_color(w.left) == "BLACK"
                    and self._get_color(w.right) == "BLACK"
                ):
                    self._set_color(w, "RED")
                    x = x.parent
                else:
                    if self._get_color(w.right) == "BLACK":
                        self._set_color(w.left, "BLACK")
                        self._set_color(w, "RED")
                        self._rotate_right(w)
                        w = x.parent.right

                    self._set_color(w, self._get_color(x.parent))
                    self._set_color(x.parent, "BLACK")
                    self._set_color(w.right, "BLACK")
                    self._rotate_left(x.parent)
                    x = self.root  # Завершаем цикл
            else:  # Симметричный случай
                w = x.parent.left
                if self._get_color(w) == "RED":
                    self._set_color(w, "BLACK")
                    self._set_color(x.parent, "RED")
                    self._rotate_right(x.parent)
                    w = x.parent.left

                if (
                    self._get_color(w.right) == "BLACK"
                    and self._get_color(w.left) == "BLACK"
                ):
                    self._set_color(w, "RED")
                    x = x.parent
                else:
                    if self._get_color(w.left) == "BLACK":
                        self._set_color(w.right, "BLACK")
                        self._set_color(w, "RED")
                        self._rotate_left(w)
                        w = x.parent.left

                    self._set_color(w, self._get_color(x.parent))
                    self._set_color(x.parent, "BLACK")
                    self._set_color(w.left, "BLACK")
                    self._rotate_right(x.parent)
                    x = self.root

        self._set_color(x, "BLACK")
