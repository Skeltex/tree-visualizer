"""Графический интерфейс главного окна."""

import json
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
    QSlider,
    QFileDialog,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter

from core.bst import BST
from core.avl_tree import AVLTree
from core.rb_tree import RBTree
from core.splay_tree import SplayTree
from gui.scene import TreeScene
from controller.animator import Animator


class TreeGraphicsView(QGraphicsView):
    """Кастомный виджет для отображения сцены с поддержкой масштабирования."""

    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        # Масштабирование будет происходить относительно курсора мыши
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    def wheelEvent(self, event):
        """Обрабатывает прокрутку колесика мыши для зума."""
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.scale(zoom_factor, zoom_factor)


class MainWindow(QMainWindow):
    """Главное окно приложения визуализации деревьев."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Интерактивный Визуализатор Деревьев Поиска")

        self.tree = None
        self.animator = None

        self.init_ui()
        self.change_tree_type()

        # self.setMinimumSize(800, 600)
        self.showMaximized()

    def init_ui(self):
        """Инициализирует элементы пользовательского интерфейса и их расположение."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        top_panel = QHBoxLayout()
        bottom_panel = QHBoxLayout()

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
        top_panel.addWidget(QLabel("Тип дерева:"))
        top_panel.addWidget(self.tree_selector)

        self.val_input = QSpinBox()
        self.val_input.setRange(-999, 999)
        self.val_input.setValue(10)
        self.val_input.setMinimumWidth(80)
        top_panel.addWidget(QLabel("Значение:"))
        top_panel.addWidget(self.val_input)

        self.btn_insert = QPushButton("Вставить")
        self.btn_insert.clicked.connect(self.on_insert)
        self.btn_delete = QPushButton("Удалить")
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_search = QPushButton("Найти")
        self.btn_search.clicked.connect(self.on_search)
        self.btn_clear = QPushButton("Очистить")
        self.btn_clear.clicked.connect(self.on_clear)

        top_panel.addWidget(self.btn_insert)
        top_panel.addWidget(self.btn_delete)
        top_panel.addWidget(self.btn_search)
        top_panel.addWidget(self.btn_clear)

        self.btn_save = QPushButton("Сохранить")
        self.btn_save.clicked.connect(self.on_save)
        self.btn_load = QPushButton("Загрузить")
        self.btn_load.clicked.connect(self.on_load)

        self.btn_pre = QPushButton("Прямой обход")
        self.btn_pre.clicked.connect(lambda: self.on_traverse("pre"))
        self.btn_in = QPushButton("Симметричный")
        self.btn_in.clicked.connect(lambda: self.on_traverse("in"))
        self.btn_post = QPushButton("Обратный")
        self.btn_post.clicked.connect(lambda: self.on_traverse("post"))

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(100, 1500)
        self.speed_slider.setValue(400)
        self.speed_slider.setInvertedAppearance(True)
        self.speed_slider.setMinimumWidth(100)
        self.speed_label = QLabel("Скорость:")
        self.speed_slider.valueChanged.connect(self.on_speed_changed)

        bottom_panel.addWidget(self.btn_save)
        bottom_panel.addWidget(self.btn_load)
        bottom_panel.addWidget(self.btn_pre)
        bottom_panel.addWidget(self.btn_in)
        bottom_panel.addWidget(self.btn_post)
        bottom_panel.addWidget(self.speed_label)
        bottom_panel.addWidget(self.speed_slider)

        main_layout.addLayout(top_panel)
        main_layout.addLayout(bottom_panel)

        self.control_buttons = [
            self.btn_insert,
            self.btn_delete,
            self.btn_search,
            self.btn_clear,
            self.btn_save,
            self.btn_load,
            self.btn_pre,
            self.btn_in,
            self.btn_post,
            self.tree_selector,
        ]

        self.scene = TreeScene()
        self.scene.node_delete_requested.connect(self.handle_right_click_delete)
        self.view = TreeGraphicsView(self.scene)
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

        current_speed = (
            self.speed_slider.value() if hasattr(self, "speed_slider") else 400
        )

        self.animator = Animator(self.scene, self.tree, speed_ms=current_speed)
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

    def on_save(self):
        """Сохраняет ключи дерева в JSON файл (тихий прямой обход)."""
        if not self.tree.root:
            QMessageBox.information(self, "Ошибка", "Дерево пустое, нечего сохранять!")
            return

        def get_keys_silent(node):
            if not node:
                return []
            return [node.key] + get_keys_silent(node.left) + get_keys_silent(node.right)

        keys = get_keys_silent(self.tree.root)

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить дерево", "", "JSON Files (*.json)"
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump({"keys": keys}, f, indent=4)
                QMessageBox.information(
                    self, "Успех", f"Дерево сохранено ({len(keys)} узлов)."
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}"
                )

    def on_load(self):
        """Загружает ключи из JSON файла и красиво анимирует построение дерева."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Загрузить дерево", "", "JSON Files (*.json)"
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                keys = data.get("keys", [])
                if not keys:
                    QMessageBox.warning(
                        self, "Ошибка", "Файл пуст или имеет неверный формат."
                    )
                    return

                self.on_clear()
                self.lock_ui()

                for key in keys:
                    self.tree.insert(key)

                self.animator.play()

            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка", f"Не удалось загрузить файл:\n{str(e)}"
                )
                self.unlock_ui()

    def handle_right_click_delete(self, key: int):
        """Обрабатывает запрос на удаление узла по правому клику мыши на сцене."""
        if not self.btn_delete.isEnabled():
            return

        self.val_input.setValue(key)
        self.on_delete()

    def on_clear(self):
        """Очищает дерево и сцену, создавая новую пустую структуру текущего типа."""
        self.change_tree_type()

    def on_speed_changed(self, value: int):
        """Обновляет скорость анимации в реальном времени."""
        if self.animator:
            self.animator.speed_ms = value
