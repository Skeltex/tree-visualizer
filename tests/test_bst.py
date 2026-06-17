import pytest
from core.bst import BST


# --- ФИКСТУРЫ ---
# Фикстура создает свежее дерево перед каждым тестом
@pytest.fixture
def bst_tree():
    tree = BST()
    for val in [10, 5, 15, 2, 7, 12, 20]:
        tree.insert(val)
    return tree


# --- ТЕСТЫ ---


def test_insert_and_search(bst_tree):
    """Проверка того, что узлы вставляются и находятся корректно."""
    # Эти элементы были вставлены фикстурой
    assert bst_tree.search(10) is not None
    assert bst_tree.search(10).key == 10

    assert bst_tree.search(7) is not None
    assert bst_tree.search(7).key == 7

    # Этого элемента нет в дереве
    assert bst_tree.search(99) is None


def test_in_order_traversal(bst_tree):
    """
    Симметричный обход (LNR) бинарного дерева поиска
    всегда должен возвращать отсортированный массив.
    """
    result = [node.key for node in bst_tree.in_order(bst_tree.root)]
    assert result == [2, 5, 7, 10, 12, 15, 20]


def test_delete_leaf_node(bst_tree):
    """Проверка удаления узла без потомков (листа)."""
    assert bst_tree.delete(2) is True
    assert bst_tree.search(2) is None

    # Проверяем, что родитель (5) потерял левого потомка
    node_5 = bst_tree.search(5)
    assert node_5.left is None


def test_delete_node_with_two_children(bst_tree):
    """Проверка сложного случая: удаление узла с 2 потомками."""
    # Удаляем корень (10)
    assert bst_tree.delete(10) is True

    # По алгоритму Кормена, на место 10 должен был встать минимум
    # из правого поддерева, то есть 12.
    assert bst_tree.root.key == 12

    # Проверяем, что обход все еще дает отсортированный массив (структура не сломалась)
    result = [node.key for node in bst_tree.in_order(bst_tree.root)]
    assert result == [2, 5, 7, 12, 15, 20]
