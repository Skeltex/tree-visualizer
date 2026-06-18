"""Графический интерфейс главного окна."""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QSpinBox,
    QGraphicsView,
    QLabel,
    QMessageBox,
)
from PySide6.QtGui import QPainter

from core.bst import BST
from core.avl_tree import AVLTree
from core.rb_tree import RBTree
from core.splay_tree import SplayTree
from gui.scene import TreeScene
from controller.animator import Animator


class MainWindow(QMainWindow):
    """Главное окно приложения визуализации деревьев."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Интерактивный Визуализатор Деревьев Поиска")
        self.resize(1200, 800)

        self.tree = None
        self.animator = None

        self.init_ui()
        self.change_tree_type()

    def init_ui(self):
        """Инициализирует элементы пользовательского интерфейса и их расположение."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        control_panel = QHBoxLayout()
        self.tree_selector = QComboBox()
        self.tree_selector.addItems(
            [
                "Бинарное дерево (BST)",
                "AVL-дерево",
                "Красно-чёрное дерево",
                "Splay-дерево",
            ]
        )
        self.tree_selector.currentIndexChanged.connect(self.change_tree_type)
        control_panel.addWidget(QLabel("Тип дерева:"))
        control_panel.addWidget(self.tree_selector)

        self.val_input = QSpinBox()
        self.val_input.setRange(-999, 999)
        self.val_input.setValue(10)
        self.val_input.setMinimumWidth(80)
        control_panel.addWidget(QLabel("Значение:"))
        control_panel.addWidget(self.val_input)
        self.btn_insert = QPushButton("Вставить")
        self.btn_insert.clicked.connect(self.on_insert)

        self.btn_delete = QPushButton("Удалить")
        self.btn_delete.clicked.connect(self.on_delete)

        self.btn_search = QPushButton("Найти")
        self.btn_search.clicked.connect(self.on_search)

        self.btn_clear = QPushButton("Очистить")
        self.btn_clear.clicked.connect(self.on_clear)

        control_panel.addWidget(self.btn_insert)
        control_panel.addWidget(self.btn_delete)
        control_panel.addWidget(self.btn_search)
        control_panel.addWidget(self.btn_clear)

        self.btn_pre = QPushButton("Прямой обход")
        self.btn_pre.clicked.connect(lambda: self.on_traverse("pre"))

        self.btn_in = QPushButton("Симметричный")
        self.btn_in.clicked.connect(lambda: self.on_traverse("in"))

        self.btn_post = QPushButton("Обратный")
        self.btn_post.clicked.connect(lambda: self.on_traverse("post"))

        control_panel.addWidget(self.btn_pre)
        control_panel.addWidget(self.btn_in)
        control_panel.addWidget(self.btn_post)

        self.control_buttons = [
            self.btn_insert,
            self.btn_delete,
            self.btn_search,
            self.btn_clear,
            self.btn_pre,
            self.btn_in,
            self.btn_post,
            self.tree_selector,
        ]

        main_layout.addLayout(control_panel)

        self.scene = TreeScene()
        self.scene.node_delete_requested.connect(self.handle_right_click_delete)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        main_layout.addWidget(self.view)

    def change_tree_type(self):
        """Вызывается при смене типа дерева в выпадающем списке."""
        self.scene.clear_scene()

        idx = self.tree_selector.currentIndex()
        if idx == 0:
            self.tree = BST()
        elif idx == 1:
            self.tree = AVLTree()
        elif idx == 2:
            self.tree = RBTree()
        elif idx == 3:
            self.tree = SplayTree()

        self.animator = Animator(self.scene, self.tree, speed_ms=400)
        self.animator.sequence_finished.connect(self.unlock_ui)

    def lock_ui(self):
        """Блокирует кнопки, пока идет анимация."""
        for btn in self.control_buttons:
            btn.setEnabled(False)

    def unlock_ui(self):
        """Разблокирует кнопки после завершения анимации."""
        for btn in self.control_buttons:
            btn.setEnabled(True)

    def on_insert(self):
        """Обрабатывает нажатие кнопки 'Вставить'."""
        val = self.val_input.value()
        self.lock_ui()
        self.tree.insert(val)
        self.animator.play()

    def on_delete(self):
        """Обрабатывает нажатие кнопки 'Удалить'."""
        val = self.val_input.value()
        self.lock_ui()
        success = self.tree.delete(val)
        if not success:
            QMessageBox.information(self, "Результат", f"Узел {val} не найден!")
        self.animator.play()

    def on_search(self):
        """Обрабатывает нажатие кнопки 'Найти'."""
        val = self.val_input.value()
        self.lock_ui()
        self.tree.search(val)
        self.animator.play()

    def on_traverse(self, mode: str):
        """Обрабатывает обход дерева в указанном порядке (pre, in, post)."""
        if not self.tree.root:
            QMessageBox.information(self, "Ошибка", "Дерево пустое!")
            return

        self.lock_ui()
        if mode == "pre":
            list(self.tree.pre_order(self.tree.root))
        elif mode == "in":
            list(self.tree.in_order(self.tree.root))
        elif mode == "post":
            list(self.tree.post_order(self.tree.root))

        self.animator.play()

    def handle_right_click_delete(self, key: int):
        """Обрабатывает запрос на удаление узла по правому клику мыши на сцене."""
        if not self.btn_delete.isEnabled():
            return

        self.val_input.setValue(key)
        self.on_delete()

    def on_clear(self):
        """Очищает дерево и сцену, создавая новую пустую структуру текущего типа."""
        self.change_tree_type()
