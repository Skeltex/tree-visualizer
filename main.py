import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    # Создаем экземпляр приложения
    app = QApplication(sys.argv)

    # Применяем темную тему (по желанию, Qt поддерживает системные темы)
    app.setStyle("Fusion")

    # Создаем и показываем главное окно
    window = MainWindow()
    window.show()

    # Запускаем бесконечный цикл обработки событий
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
