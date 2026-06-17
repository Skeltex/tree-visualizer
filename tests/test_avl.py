import pytest
from core.avl_tree import AVLTree

# --- Вспомогательные функции для тестов ---


def assert_avl_invariants(tree: AVLTree):
    """
    Рекурсивная проверка главного свойства AVL-дерева:
    Разница высот между левым и правым поддеревом любого узла не превышает 1.
    Также проверяет корректность сохранения высоты в meta['height'].
    """

    def check_node(node):
        if not node:
            return 0

        left_h = check_node(node.left)
        right_h = check_node(node.right)

        # 1. Проверка баланса (Главное правило AVL)
        balance_factor = left_h - right_h
        assert abs(balance_factor) <= 1, (
            f"Узел {node.key} разбалансирован! BF = {balance_factor}"
        )

        # 2. Проверка правильности подсчета высоты
        actual_height = 1 + max(left_h, right_h)
        stored_height = node.meta.get("height", 1)
        assert stored_height == actual_height, (
            f"Узел {node.key}: сохраненная высота {stored_height} != реальной {actual_height}"
        )

        # 3. Проверка свойства поиска (BST)
        if node.left:
            assert node.left.key < node.key
        if node.right:
            assert node.right.key > node.key

        return actual_height

    check_node(tree.root)


@pytest.fixture
def avl():
    """Фикстура, выдающая пустое дерево перед каждым тестом."""
    return AVLTree()


# --- Тесты ротаций (Вставка) ---


def test_right_rotation(avl):
    """Случай Left-Left (Требует Правого поворота)."""
    # Вставляем по убыванию: 30 -> 20 -> 10
    avl.insert(30)
    avl.insert(20)
    avl.insert(10)

    # 20 должен стать корнем, 10 слева, 30 справа
    assert avl.root.key == 20
    assert avl.root.left.key == 10
    assert avl.root.right.key == 30
    assert_avl_invariants(avl)


def test_left_rotation(avl):
    """Случай Right-Right (Требует Левого поворота)."""
    # Вставляем по возрастанию: 10 -> 20 -> 30
    avl.insert(10)
    avl.insert(20)
    avl.insert(30)

    assert avl.root.key == 20
    assert avl.root.left.key == 10
    assert avl.root.right.key == 30
    assert_avl_invariants(avl)


def test_left_right_rotation(avl):
    """Случай Left-Right (Зигзаг, требует двойного поворота)."""
    avl.insert(30)
    avl.insert(10)
    avl.insert(20)  # Этот элемент "вклинивается" посередине

    assert avl.root.key == 20
    assert avl.root.left.key == 10
    assert avl.root.right.key == 30
    assert_avl_invariants(avl)


def test_right_left_rotation(avl):
    """Случай Right-Left (Зигзаг, требует двойного поворота)."""
    avl.insert(10)
    avl.insert(30)
    avl.insert(20)

    assert avl.root.key == 20
    assert avl.root.left.key == 10
    assert avl.root.right.key == 30
    assert_avl_invariants(avl)


# --- Нагрузочные тесты и Удаление ---


def test_sequential_insert_stress(avl):
    """
    Вставка 15 элементов по порядку.
    В обычном BST это была бы "сосиска" (список) высотой 15.
    В AVL-дереве из 15 элементов (идеально сбалансированном) высота должна быть ровно 4.
    """
    for i in range(1, 16):
        avl.insert(i)

    assert avl.root.key == 8  # 8 должно вынырнуть в самый верх
    assert avl.root.meta["height"] == 4
    assert_avl_invariants(avl)


def test_delete_triggering_rebalance(avl):
    """Проверка того, что удаление узла вызывает перебалансировку."""
    # Создаем дерево, перевешивающее вправо
    for val in [20, 10, 30, 40, 50]:
        avl.insert(val)

    # Дерево сейчас: корень 20, слева 10, справа 40 (и его дети 30, 50)
    assert avl.root.key == 20

    # Удаляем левый узел. Теперь правая сторона слишком тяжелая!
    # Должен произойти Левый поворот вокруг корня.
    avl.delete(10)

    # Корень должен смениться
    assert avl.root.key == 40
    assert avl.root.left.key == 20
    assert avl.root.right.key == 50
    assert_avl_invariants(avl)
