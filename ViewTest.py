import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsView,
                             QGraphicsScene, QVBoxLayout, QHBoxLayout,
                             QWidget, QPushButton, QGraphicsRectItem)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPointF
from PyQt6.QtGui import QBrush, QColor, QPen


class SeamlessGraphicsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Бесшовные графические сцены")
        self.setGeometry(100, 100, 1000, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)  # Убираем промежуток между видами

        # Создаем графические сцены
        self.scene1 = QGraphicsScene()
        self.scene2 = QGraphicsScene()

        # Заполняем сцены содержимым
        self.setup_scene(self.scene1, QColor(100, 150, 200), "Сцена 1")
        self.setup_scene(self.scene2, QColor(200, 150, 100), "Сцена 2")

        # Создаем виды с отключенными рамками и скроллбарами
        self.view1 = QGraphicsView(self.scene1)
        self.view2 = QGraphicsView(self.scene2)

        # Настраиваем виды для бесшовного отображения
        for view in [self.view1, self.view2]:
            view.setFrameStyle(0)  # Убираем рамку
            view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        # Добавляем виды в layout
        layout.addWidget(self.view1, 1)
        layout.addWidget(self.view2, 1)

        # Кнопка для переключения
        self.toggle_button = QPushButton("Переключить сцены")
        self.toggle_button.clicked.connect(self.toggle_scenes)
        layout.addWidget(self.toggle_button)

        # Анимация
        self.animation = QPropertyAnimation(self.view2, b"pos")
        self.animation.setDuration(800)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.is_scene2_visible = False

    def setup_scene(self, scene, color, text):
        # Создаем фон
        rect = QGraphicsRectItem(0, 0, 400, 400)
        rect.setBrush(QBrush(color))
        rect.setPen(QPen(Qt.PenStyle.NoPen))
        scene.addItem(rect)

        # Добавляем текст
        text_item = scene.addText(text)
        text_item.setDefaultTextColor(QColor(255, 255, 255))
        text_item.setPos(150, 180)

    def toggle_scenes(self):
        if self.is_scene2_visible:
            # Прячем сцену 2
            self.animation.setStartValue(self.view2.pos())
            self.animation.setEndValue(QPointF(self.width(), 0))
            self.is_scene2_visible = False
        else:
            # Показываем сцену 2
            self.view2.move(self.width(), 0)  # Начинаем за пределами экрана
            self.animation.setStartValue(QPointF(self.width(), 0))
            self.animation.setEndValue(QPointF(0, 0))
            self.is_scene2_visible = True

        self.animation.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SeamlessGraphicsWindow()
    window.show()
    sys.exit(app.exec())