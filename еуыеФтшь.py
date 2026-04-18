from PyQt6.QtWidgets import (QApplication, QGraphicsScene, QGraphicsView,
                             QGraphicsLineItem, QVBoxLayout, QWidget, QPushButton)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPen
import sys


class LineAnimationController(QWidget):
    def __init__(self):
        super().__init__()
        self.is_playing = False
        self.line_x = 50
        self.speed = 3
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Создание сцены
        self.scene = QGraphicsScene(0, 0, 800, 400)

        # Создание линии
        self.line_item = QGraphicsLineItem(self.line_x, 200, self.line_x + 100, 200)
        self.line_item.setPen(QPen(Qt.GlobalColor.blue, 2))
        self.scene.addItem(self.line_item)

        # Создание view
        self.view = QGraphicsView(self.scene)

        # Кнопка управления
        self.btn_play = QPushButton("Старт")
        self.btn_play.clicked.connect(self.toggle_animation)

        # Таймер для анимации
        self.timer = QTimer()
        self.timer.timeout.connect(self.move_line)

        layout.addWidget(self.view)
        layout.addWidget(self.btn_play)
        self.setLayout(layout)

        self.setWindowTitle("Анимация линии")
        self.resize(900, 500)

    def toggle_animation(self):
        if not self.is_playing:
            self.start_animation()
        else:
            self.stop_animation()

    def start_animation(self):
        self.is_playing = True
        self.btn_play.setText("Стоп")
        self.timer.start(30)  # Интервал в миллисекундах

    def stop_animation(self):
        self.is_playing = False
        self.btn_play.setText("Старт")
        self.timer.stop()

    def move_line(self):
        self.line_x += self.speed

        # Если линия вышла за границы, возвращаем в начало
        if self.line_x > 700:
            self.line_x = 50

        # Обновляем позицию линии
        self.line_item.setLine(self.line_x, 200, self.line_x + 100, 200)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LineAnimationController()
    window.show()
    sys.exit(app.exec())