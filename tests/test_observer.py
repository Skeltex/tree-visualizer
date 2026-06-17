from unittest.mock import MagicMock
from core.avl_tree import AVLTree
from core.base_tree import EventType


def test_avl_emits_rotate_event():
    """Проверяем, что при балансировке дерево отправляет сигнал ROTATE."""
    tree = AVLTree()

    # Создаем фейкового слушателя и подписываем его на дерево
    mock_observer = MagicMock()
    tree.add_observer(mock_observer)

    # Вставляем узлы так, чтобы спровоцировать Правый поворот (Left-Left case)
    tree.insert(30)
    tree.insert(20)
    tree.insert(10)

    # Извлекаем все типы событий, которые были отправлены шпиону
    # call.args[0] - это первый аргумент, переданный в observer (EventType)
    emitted_events = [call.args[0] for call in mock_observer.call_args_list]

    # Проверяем, что дерево сообщало о вставках
    assert EventType.INSERT in emitted_events

    # ГЛАВНОЕ: Проверяем, что дерево сообщило о повороте!
    assert EventType.ROTATE in emitted_events

    # Проверяем детали события ROTATE
    rotate_calls = [
        call
        for call in mock_observer.call_args_list
        if call.args[0] == EventType.ROTATE
    ]
    assert len(rotate_calls) > 0

    # Проверяем, что в kwargs было передано правильное направление
    assert rotate_calls[0].kwargs.get("direction") == "RIGHT"


def test_bst_emits_found_not_found():
    """Проверяем события поиска."""
    tree = AVLTree()
    tree.insert(10)

    mock_observer = MagicMock()
    tree.add_observer(mock_observer)

    tree.search(10)  # Успешный поиск
    tree.search(99)  # Неуспешный поиск

    emitted_events = [call.args[0] for call in mock_observer.call_args_list]

    assert EventType.FOUND in emitted_events
    assert EventType.NOT_FOUND in emitted_events
