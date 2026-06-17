import pytest
from core.splay_tree import SplayTree

# --- Вспомогательные функции ---


def assert_bst_invariants(node):
    """
    Поскольку Splay-дерево не имеет баланса или цветов,
    мы проверяем только базовое свойство бинарного поиска
    (левый меньше, правый больше) после всех безумных ротаций.
    """
    if not node:
        return

    if node.left:
        assert node.left.key < node.key, (
            f"Ошибка: левый потомок {node.left.key} >= родителя {node.key}"
        )
        # Проверяем, что связь двусторонняя (важно после ротаций!)
        assert node.left.parent == node
        assert_bst_invariants(node.left)

    if node.right:
        assert node.right.key > node.key, (
            f"Ошибка: правый потомок {node.right.key} <= родителя {node.key}"
        )
        assert node.right.parent == node
        assert_bst_invariants(node.right)


@pytest.fixture
def splay():
    """Выдает чистое Splay-дерево для каждого теста."""
    return SplayTree()


# --- ТЕСТЫ ВСТАВКИ И ПОИСКА ---


def test_insert_splays_to_root(splay):
    """Каждый вставленный элемент обязан становиться новым корнем."""
    splay.insert(10)
    assert splay.root.key == 10

    splay.insert(20)
    assert splay.root.key == 20
    assert splay.root.left.key == 10  # 10 ушло влево (Zig поворот)

    splay.insert(15)
    assert splay.root.key == 15
    # Дерево должно быть корректным BST
    assert_bst_invariants(splay.root)


def test_search_splays_to_root(splay):
    """Успешный поиск должен поднимать найденный элемент в корень."""
    # Вставляем элементы
    for val in [10, 20, 30, 40, 50]:
        splay.insert(val)

    # Сейчас 50 - это корень (т.к. вставлен последним)
    assert splay.root.key == 50

    # Ищем самый глубокий элемент
    node = splay.search(10)

    # 10 должен "всплыть" на самый верх
    assert node is not None
    assert splay.root.key == 10
    assert_bst_invariants(splay.root)


def test_search_not_found_splays_last_accessed(splay):
    """
    Если элемент не найден, в корень должен подняться
    ПОСЛЕДНИЙ просмотренный узел.
    """
    splay.insert(10)
    splay.insert(30)
    splay.insert(20)  # Корень = 20

    # Ищем 25. Путь поиска: 20 -> направо к 30 -> налево (None)
    # Последний просмотренный узел: 30. Он должен стать корнем.
    node = splay.search(25)

    assert node is None
    assert splay.root.key == 30
    assert_bst_invariants(splay.root)


# --- ТЕСТЫ СПЕЦИФИЧНЫХ РОТАЦИЙ (ZIG-ZIG, ZIG-ZAG) ---


def test_zig_zig_rotation(splay):
    """
    Проверка Zig-Zig поворота.
    Случается, когда узел и его родитель - оба левые (или оба правые) дети.
    """
    # Создаем структуру вручную через вставку в обычное BST (чтобы избежать splay)
    # Но проще смоделировать через обычные вставки и поиск:
    splay.insert(30)
    splay.insert(20)
    splay.insert(10)  # Вызовет Zig-Zig

    assert splay.root.key == 10
    assert splay.root.right.key == 20
    assert splay.root.right.right.key == 30
    assert_bst_invariants(splay.root)


def test_zig_zag_rotation(splay):
    """
    Проверка Zig-Zag поворота.
    Случается, когда узел - правый ребенок, а его родитель - левый (или наоборот).
    """
    splay.insert(30)
    splay.insert(10)
    splay.insert(20)  # Вызовет Zig-Zag

    assert splay.root.key == 20
    assert splay.root.left.key == 10
    assert splay.root.right.key == 30
    assert_bst_invariants(splay.root)


# --- ТЕСТЫ УДАЛЕНИЯ ---


def test_delete_splays_and_merges(splay):
    """
    При удалении узел поднимается в корень, корень удаляется,
    а два поддерева сливаются (максимум левого становится новым корнем).
    """
    for val in [20, 10, 30, 5, 15, 25, 35]:
        splay.insert(val)

    # Ищем 15, чтобы оно стало корнем (просто для усложнения структуры)
    splay.search(15)

    # Удаляем 20
    assert splay.delete(20) is True

    # Проверяем, что 20 удалено
    assert splay.search(20) is None

    # Дерево должно остаться корректным бинарным деревом поиска
    assert_bst_invariants(splay.root)

    # Длина симметричного обхода должна уменьшиться ровно на 1
    result = [node.key for node in splay.in_order(splay.root)]
    assert result == [5, 10, 15, 25, 30, 35]


def test_delete_root_without_left_child(splay):
    """Случай слияния, когда у удаляемого корня нет левого поддерева."""
    splay.insert(10)
    splay.insert(20)
    splay.insert(30)  # Корень = 30, левое дерево = 20 -> 10, правого нет

    # Удаляем 10 (поднимется в корень, затем удалится)
    splay.delete(10)

    assert_bst_invariants(splay.root)
    result = [node.key for node in splay.in_order(splay.root)]
    assert result == [20, 30]
