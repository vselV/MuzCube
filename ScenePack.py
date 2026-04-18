from PyQt6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene,
                             QGraphicsProxyWidget, QGraphicsRectItem, QVBoxLayout, QWidget)
from PyQt6.QtCore import Qt
import sys


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Основная сцена
        self.main_scene = QGraphicsScene()
        self.main_view = QGraphicsView(self.main_scene)

        # Вложенная сцена (будет отображаться как объект в основной сцене)
        self.nested_scene = QGraphicsScene()
        self.nested_view = QGraphicsView(self.nested_scene)

        # Добавляем элементы во вложенную сцену
        rect = QGraphicsRectItem(0, 0, 100, 100)
        rect.setBrush(Qt.GlobalColor.red)
        self.nested_scene.addItem(rect)

        # Создаем прокси-виджет для вложенного view
        proxy = QGraphicsProxyWidget()
        proxy.setWidget(self.nested_view)
        proxy.setPos(50, 50)

        # Добавляем прокси в основную сцену
        self.main_scene.addItem(proxy)

        # Настройка layout
        layout = QVBoxLayout()
        layout.addWidget(self.main_view)
        self.setLayout(layout)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
