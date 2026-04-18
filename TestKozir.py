import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsView,
                             QGraphicsScene, QWidget, QVBoxLayout,
                             QPushButton, QLabel)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QBrush, QColor


class OverlayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        # Устанавливаем стиль для полупрозрачного фона
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(240, 240, 240, 200);
                border: 1px solid #cccccc;
                border-radius: 5px;
            }
        """)

        # Устанавливаем флаги, чтобы виджет был поверх всего
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.SubWindow | Qt.WindowType.FramelessWindowHint)

        # Создаем layout для козырька
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Добавляем элементы меню
        label = QLabel("Меню")
        button1 = QPushButton("Опция 1")
        button2 = QPushButton("Опция 2")
        button3 = QPushButton("Опция 3")

        layout.addWidget(label)
        layout.addWidget(button1)
        layout.addWidget(button2)
        layout.addWidget(button3)

        # Устанавливаем фиксированный размер
        self.setFixedSize(150, 200)


class GraphicsSceneWithOverlay(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_scene()
        self.setup_overlay()

    def setup_scene(self):
        # Создаем сцену
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Добавляем тестовые элементы на сцену
        rect = self.scene.addRect(QRectF(0, 0, 200, 200),
                                  brush=QBrush(QColor(100, 150, 200)))
        ellipse = self.scene.addEllipse(QRectF(250, 50, 150, 150),
                                        brush=QBrush(QColor(200, 100, 100)))

        # Устанавливаем размер сцены
        self.scene.setSceneRect(0, 0, 800, 600)

    def setup_overlay(self):
        # Создаем козырек
        self.overlay = OverlayWidget(self)

        # Позиционируем козырек в правом верхнем углу
        self.position_overlay()

        # Показываем козырек
        self.overlay.show()

    def position_overlay(self):
        # Получаем размеры view
        view_width = self.width()

        # Позиционируем козырек в правом верхнем углу с отступом 10px
        overlay_x = view_width - self.overlay.width() - 10
        self.overlay.move(overlay_x, 10)

    def resizeEvent(self, event):
        # При изменении размера перепозиционируем козырек
        super().resizeEvent(event)
        self.position_overlay()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Сцена с козырьком")
        self.setGeometry(100, 100, 800, 600)

        # Создаем основной виджет
        self.graphics_view = GraphicsSceneWithOverlay()
        self.setCentralWidget(self.graphics_view)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())