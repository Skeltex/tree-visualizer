import pytest
from core.rb_tree import RBTree

# --- Вспомогательные функции для тестов ---


def assert_rb_invariants(tree: RBTree):
    """
    Рекурсивная проверка всех свойств Красно-чёрного дерева.
    """
    if not tree.root:
        return

    # Правило 1: Корень всегда черный
    assert tree._get_color(tree.root) == "BLACK", "Ошибка: Корень дерева не черный!"

    def check_node(node) -> int:
        """
        Проверяет узел и возвращает 'черную высоту' этого поддерева.
        """
        # Листья (None) по правилам RB-дерева считаются черными (высота = 1)
        if not node:
            return 1

        color = tree._get_color(node)

        # Свойство обычного BST
        if node.left:
            assert node.left.key < node.key, (
                f"Ошибка BST: {node.left.key} >= {node.key}"
            )
        if node.right:
            assert node.right.key > node.key, (
                f"Ошибка BST: {node.right.key} <= {node.key}"
            )

        # Правило 2: У красного узла не может быть красных детей
        if color == "RED":
            left_color = tree._get_color(node.left)
            right_color = tree._get_color(node.right)
            assert left_color == "BLACK", (
                f"Ошибка цвета: У красного узла {node.key} левый потомок красный!"
            )
            assert right_color == "BLACK", (
                f"Ошибка цвета: У красного узла {node.key} правый потомок красный!"
            )

        # Рекурсивно вычисляем черную высоту левого и правого поддеревьев
        left_black_height = check_node(node.left)
        right_black_height = check_node(node.right)

        # Правило 3: Черная высота веток должна совпадать
        assert left_black_height == right_black_height, (
            f"Нарушение черной высоты у узла {node.key}: слева {left_black_height}, справа {right_black_height}"
        )

        # Возвращаем черную высоту текущего поддерева
        return left_black_height + (1 if color == "BLACK" else 0)

    # Запускаем проверку с корня
    check_node(tree.root)


@pytest.fixture
def rb():
    """Фикстура для выдачи свежего дерева."""
    return RBTree()


# --- ТЕСТЫ ---


def test_insert_root_is_black(rb):
    """При вставке первого элемента он должен стать черным корнем."""
    rb.insert(10)
    assert rb.root.key == 10
    assert rb._get_color(rb.root) == "BLACK"
    assert_rb_invariants(rb)


def test_insert_recolor(rb):
    """
    Проверка перекраски (Дядя красный).
    Если вставить 10(B), 5(R), 15(R) и затем 2(R), то 5 и 15
    должны перекраситься в черные, а корень остаться черным.
    """
    rb.insert(10)
    rb.insert(5)
    rb.insert(15)
    rb.insert(2)  # Вызывает перекраску

    assert rb._get_color(rb.search(5)) == "BLACK"
    assert rb._get_color(rb.search(15)) == "BLACK"
    assert rb._get_color(rb.search(2)) == "RED"
    assert_rb_invariants(rb)


def test_insert_rotations(rb):
    """
    Проверка ротаций (Дядя черный).
    Вставляем по убыванию: 30, 20, 10. Должен произойти правый поворот.
    """
    rb.insert(30)
    rb.insert(20)
    rb.insert(10)

    # 20 становится корнем, 10 и 30 - потомками
    assert rb.root.key == 20
    assert rb._get_color(rb.root) == "BLACK"
    assert rb._get_color(rb.search(10)) == "RED"
    assert rb._get_color(rb.search(30)) == "RED"
    assert_rb_invariants(rb)


def test_delete_red_leaf(rb):
    """
    Удаление красного листа не меняет черную высоту,
    поэтому балансировка не требуется.
    """
    rb.insert(10)  # Корень (B)
    rb.insert(5)  # Левый (R)
    rb.insert(15)  # Правый (R)

    # Удаляем красный узел
    rb.delete(5)

    assert rb.search(5) is None
    assert_rb_invariants(rb)


def test_delete_black_node_complex(rb):
    """
    Сложное удаление черного узла (вызывает Двойной Черный и _delete_fixup).
    """
    # Создаем дерево побольше
    elements = [20, 10, 30, 5, 15, 25, 35]
    for el in elements:
        rb.insert(el)

    assert_rb_invariants(rb)

    # Удаляем черный корень
    rb.delete(20)
    assert_rb_invariants(rb)

    # Удаляем другие узлы по одному и проверяем
    rb.delete(10)
    assert_rb_invariants(rb)
    rb.delete(35)
    assert_rb_invariants(rb)


def test_rb_stress_test(rb):
    """
    Нагрузочное тестирование:
    Вставляем 100 элементов и удаляем каждый третий,
    проверяя инварианты на каждом шаге.
    Это доказывает, что фантомные узлы работают идеально.
    """
    # Вставляем от 1 до 100
    for i in range(1, 101):
        rb.insert(i)
        assert_rb_invariants(rb)  # Инвариант должен сохраняться всегда

    # Удаляем элементы, кратные 3
    for i in range(3, 101, 3):
        rb.delete(i)
        assert_rb_invariants(rb)

    # Проверяем, что элементы действительно удалились
    assert rb.search(3) is None
    assert rb.search(99) is None
    assert rb.search(2) is not None  # А некратные остались
