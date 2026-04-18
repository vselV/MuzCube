from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QVariantAnimation, QEasingCurve, QPropertyAnimation
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QMouseEvent, QTransform
from PyQt6.QtWidgets import (QComboBox, QSplitter, QDockWidget, QVBoxLayout,
                             QHBoxLayout, QWidget, QScrollArea, QSizePolicy, QGraphicsView, QGraphicsScene,
                             QGraphicsLineItem, QGraphicsRectItem, QLabel, QPushButton, QGraphicsItem,
                             QStyleOptionGraphicsItem, QStyle, QGraphicsOpacityEffect, QGridLayout, QFrame)

class GridScene(QGraphicsScene):
    def __init__(self, func, parent=None):
        super().__init__(parent)
        self.x_step = 10
        self.y_step = 10
        self.func = func
