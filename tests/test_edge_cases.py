from core.bst import BST


def test_empty_tree_operations():
    """Проверка безопасности операций на пустом дереве."""
    tree = BST()

    # Поиск и удаление не должны вызывать ошибок (например, AttributeError)
    assert tree.search(10) is None
    assert tree.delete(10) is False

    # Обходы пустого дерева должны возвращать пустые списки, а не падать
    assert list(tree.in_order(tree.root)) == []
    assert list(tree.pre_order(tree.root)) == []
    assert list(tree.post_order(tree.root)) == []


def test_duplicate_insert():
    """Проверка игнорирования дубликатов."""
    tree = BST()
    node1 = tree.insert(10)
    node2 = tree.insert(10)  # Пытаемся вставить то же самое число

    assert node1 is not None
    assert node2 is None  # По нашей логике возвращается None

    # У корня не должно появиться потомков
    assert tree.root.left is None
    assert tree.root.right is None


def test_delete_only_node():
    """Удаление корня, когда он является единственным узлом."""
    tree = BST()
    tree.insert(10)

    assert tree.delete(10) is True
    assert tree.root is None


def test_delete_non_existent_node():
    """Попытка удалить узел, которого нет, не должна ломать структуру."""
    tree = BST()
    tree.insert(10)
    tree.insert(5)

    assert tree.delete(99) is False

    # Дерево должно остаться нетронутым
    assert tree.root.key == 10
    assert tree.root.left.key == 5
