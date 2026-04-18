import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsView,
                             QGraphicsScene, QGraphicsRectItem, QVBoxLayout, QWidget)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter


class SelectableRectItem(QGraphicsRectItem):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.setPen(QPen(Qt.GlobalColor.black))
        self.setBrush(QBrush(QColor(100, 150, 200)))
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)

    def setSelected(self, selected):
        super().setSelected(selected)
        if selected:
            self.setBrush(QBrush(QColor(200, 100, 100)))  # Красный при выделении
        else:
            self.setBrush(QBrush(QColor(100, 150, 200)))  # Синий обычный


class GraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.rubberBandRect = QRectF()
        self.selecting = False
        self.startPoint = QPointF()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.startPoint = self.mapToScene(event.pos())
            self.selecting = True
            self.rubberBandRect = QRectF(self.startPoint, self.startPoint)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.selecting:
            endPoint = self.mapToScene(event.pos())
            self.rubberBandRect = QRectF(self.startPoint, endPoint).normalized()
            self.viewport().update()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton and self.selecting:
            self.selectItemsInRubberBand()
            self.selecting = False
            self.rubberBandRect = QRectF()
            self.viewport().update()
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def selectItemsInRubberBand(self):
        scene = self.scene()
        for item in scene.items():
            if isinstance(item, SelectableRectItem):
                # Проверяем пересечение прямоугольника выделения с элементом
                if self.rubberBandRect.intersects(item.rect()):
                    item.setSelected(True)
                else:
                    item.setSelected(False)

    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)
        if self.selecting and not self.rubberBandRect.isNull():
            # Рисуем прямоугольник выделения
            painter.setPen(QPen(Qt.GlobalColor.red, 1, Qt.PenStyle.DashLine))
            painter.setBrush(QBrush(QColor(255, 0, 0, 50)))  # Полупрозрачная заливка
            painter.drawRect(self.rubberBandRect)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Выделение прямоугольников")
        self.setGeometry(100, 100, 800, 600)

        # Создаем сцену
        scene = QGraphicsScene(self)
        scene.setSceneRect(0, 0, 600, 400)

        # Добавляем прямоугольники
        for i in range(10):
            for j in range(8):
                rect = SelectableRectItem(i * 60 + 10, j * 50 + 10, 40, 30)
                scene.addItem(rect)

        # Создаем view
        view = GraphicsView(scene)

        # Настраиваем layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(view)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())