from core.bst import BST
from controller.animator import TreeLayout


def test_tree_layout_coordinates():
    """
    Проверяем, что алгоритм расчета координат располагает узлы так,
    что они не перекрывают друг друга (X растет слева направо, Y растет вниз).
    """
    tree = BST()
    tree.insert(20)  # Корень
    tree.insert(10)  # Левый
    tree.insert(30)  # Правый

    # Запускаем расчет координат
    layout = TreeLayout.calculate(tree.root)

    # Получаем уникальные ID узлов
    id_20 = tree.search(20).id
    id_10 = tree.search(10).id
    id_30 = tree.search(30).id

    # Правило 1: Координата X должна строго возрастать слева направо
    assert layout[id_10]["x"] < layout[id_20]["x"]
    assert layout[id_30]["x"] > layout[id_20]["x"]

    # Правило 2: Координата Y (глубина) потомков должна быть строго больше родителя
    assert layout[id_10]["y"] > layout[id_20]["y"]
    assert layout[id_30]["y"] > layout[id_20]["y"]

    # У узлов на одном уровне Y должен совпадать
    assert layout[id_10]["y"] == layout[id_30]["y"]

    # Правило 3: Привязка родителя (необходима для отрисовки линий)
    assert layout[id_20]["parent_id"] is None
    assert layout[id_10]["parent_id"] == id_20
    assert layout[id_30]["parent_id"] == id_20
