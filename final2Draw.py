import random
import sys
from PyQt6.QtCore import Qt, QRectF, QPointF, QSizeF, pyqtSignal, QTimer, QPropertyAnimation, QAbstractAnimation, \
    QEasingCurve, QTimeLine, QVariantAnimation, QParallelAnimationGroup
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QTransform, QPixmap
from PyQt6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene,
                             QGraphicsRectItem, QGraphicsItem, QVBoxLayout,
                             QHBoxLayout, QWidget, QCheckBox, QScrollBar,
                             QSlider, QLabel, QSizePolicy, QGraphicsOpacityEffect, QGraphicsWidget, QGraphicsPixmapItem,
                             QGraphicsEffect, QGraphicsTextItem)
from numpy.ma.core import floor
import math

import sys
from PyQt6.QtCore import Qt, QRectF, QPointF, QSizeF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QTransform
from PyQt6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene,
                             QGraphicsRectItem, QGraphicsItem, QVBoxLayout,
                             QHBoxLayout, QWidget, QCheckBox, QScrollBar,
                             QSlider, QLabel, QSizePolicy)


class ScaleSlider(QSlider):
    sliderWheelMoved = pyqtSignal(int)

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setRange(10, 400)
        self.setValue(100)
        self.setSingleStep(5)
        self.setPageStep(20)
        self.setTickInterval(50)
        self.setTickPosition(QSlider.TickPosition.TicksBelow)

    def wheelEvent(self, event):
        self.sliderWheelMoved.emit(event.angleDelta().y())
        event.accept()


class RectangleItem(QGraphicsRectItem):
    def __init__(self, rect, parent=None):
        super().__init__(rect, parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        # Настройки внешнего вида
        self.normal_color = QColor(100, 150, 255, 150)
        self.hover_color = QColor(100, 200, 255, 200)
        self.selected_color = QColor(255, 150, 50, 200)

        self.setBrush(QBrush(self.normal_color))
        self.setPen(QPen(Qt.GlobalColor.black, 1))

        # Настройки для изменения размера
        self.resize_area_width = 10  # Ширина невидимой области для изменения размера
        self.is_resizing_left = False
        self.is_resizing_right = False
        self.initial_rect = None

        # Эффект прозрачности для анимации
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self.opacity_effect)

        # Таймер для удаления после анимации
        self.fade_timer = QTimer()
        self.fade_timer.setSingleShot(True)
        self.fade_timer.timeout.connect(self._final_remove)
        self.removing = False

        self.text_item = None
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)

    def add_text_item(self):
        # Удаляем предыдущий текст, если есть
        if self.text_item and self.scene():
            self.scene().removeItem(self.text_item)

        # Создаем новый текстовый элемент
        self.text_item = QGraphicsTextItem("", self)
        self.text_item.setDefaultTextColor(Qt.GlobalColor.black)
        self.text_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
        self.text_item.keyPressEvent = self.text_key_press_event
        # Центрируем текст внутри прямоугольника
        #    text_rect = self.text_item.boundingRect()
        rect = self.rect()
        self.text_item.setPos(rect.x(), rect.y())

        # Даем фокус текстовому элементу для редактирования
        self.text_item.setFocus()
        self.text_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.text_item.setFocus()
        # Подключаем сигнал изменения текста (опционально)
    #    self.text_item.document().contentsChanged.connect(self.adjust_text_position)

    def adjust_text_position(self):
        """Автоматически подгоняем размер текста под прямоугольник"""

        print(self.transform().m22())

        if self.text_item:
            text_rect = self.text_item.boundingRect()
            rect = self.rect()

            # Масштабируем текст, если он не помещается
            if text_rect.width() > rect.width() or text_rect.height() > rect.height():
                print(self.transform())
                scale = min(rect.width() / text_rect.width(),
                            rect.height() / text_rect.height()) * 0.9
                self.text_item.setScale(scale)
            else:
                scale = min(rect.width() / text_rect.width() * self.transform().m22(),
                            rect.height() / text_rect.height()) * 0.9
                self.text_item.setScale(scale)

            # Перецентриру
            self.text_item.setPos(rect.x(), rect.y())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Tab and self.isSelected():
            self.add_text_item()
            event.accept()

    def text_key_press_event(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Завершаем редактирование
            self.clearFocus()
            if self.scene():
                self.scene().clearFocus()
        else:
            # Стандартная обработка для других клавиш
            QGraphicsTextItem.keyPressEvent(self.text_item, event)
    def hoverMoveEvent(self, event):
        # Изменяем курсор при наведении на области изменения размера
        rect = self.rect()
        if (event.pos().x() < rect.left() + self.resize_area_width or
                event.pos().x() > rect.right() - self.resize_area_width):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.fade_out_and_remove()
            return

        rect = self.rect()
        # Проверяем, нажали ли на области изменения размера
        if event.pos().x() < rect.left() + self.resize_area_width:
            self.is_resizing_left = True
            self.initial_rect = rect
        elif event.pos().x() > rect.right() - self.resize_area_width:
            self.is_resizing_right = True
            self.initial_rect = rect
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # print(event.scenePos().x(),self.rect().y())
        if self.is_resizing_left or self.is_resizing_right:
            # Изменяем размер прямоугольника
            new_pos = event.pos()
            # new_pos = self.pos()
            scene = self.scene()

            if scene and (scene.v_grid_enabled or scene.h_grid_enabled):
                new_pos = scene.snap_to_grid(new_pos)

            rect = self.rect()
            if self.is_resizing_left:
                # Растягиваем влево
                new_left = new_pos.x()
                new_width = self.initial_rect.right() - new_left
                if new_width > 5:  # Минимальная ширина
                    self.setRect(new_left, rect.y(), new_width, rect.height())
            elif self.is_resizing_right:
                # Растягиваем вправо
                new_right = new_pos.x()
                new_width = new_right - self.initial_rect.left()
                if new_width > 5:  # Минимальная ширина
                    self.setRect(rect.x(), rect.y(), new_width, rect.height())
        else:
            # Перемещаем прямоугольник
            super().mouseMoveEvent(event)
            print(self.scenePos(), event.scenePos())
            # Привязка к сетке при перемещении
            scene = self.scene()
            if scene and (scene.v_grid_enabled or scene.h_grid_enabled):
                snapped_pos = scene.snap_to_grid(self.pos(), bol=True)
                self.setPos(snapped_pos)

        if self.scene() and self.scene().views():
            self.scene().views()[0].viewport().update()

    def mouseReleaseEvent(self, event):
        self.is_resizing_left = False
        self.is_resizing_right = False
        self.initial_rect = None
        super().mouseReleaseEvent(event)

    def fade_out_and_remove(self):
        """Запускает анимацию затухания и удаляет элемент"""
        if not self.removing:
            self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.animation.setDuration(150)  # 200 мс длительность анимации
            self.animation.setStartValue(1.0)
            self.animation.setEndValue(0.0)
            self.animation.start()

        # Удаляем элемент после завершения анимации
        self.removing = True
        self.fade_timer.start(150)


    def _final_remove(self):
        """Финальное удаление элемента после анимации"""
        if self.scene():
            self.scene().removeItem(self)
        self.removing = False


class InfiniteScene(QGraphicsScene):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(-10000, -10000, 20000, 20000)

        self.h_grid_enabled = True
        self.v_grid_enabled = True
        self.grid_size = 50

        self.drawing = False
        self.right_button_pressed = False

        self.start_point = QPointF()
        self.current_rect = None
        self.rect_height = 30

        self.setBackgroundBrush(QBrush(QColor(240, 240, 240)))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Tab:
            selected = self.selectedItems()
            if selected and isinstance(selected[0], RectangleItem):
                selected[0].add_text_item()
                event.accept()
                return
        super().keyPressEvent(event)

    def drawBackground(self, painter, rect):
        painter.fillRect(rect, self.backgroundBrush())

        if self.h_grid_enabled or self.v_grid_enabled:
            pen = QPen(QColor(200, 200, 200), 1)
            painter.setPen(pen)

            left = int(rect.left()) - (int(rect.left()) % self.grid_size)
            top = int(rect.top()) - (int(rect.top()) % self.grid_size)
            right = int(rect.right())
            bottom = int(rect.bottom())

            if self.v_grid_enabled:
                for x in range(left, right, self.grid_size):
                    painter.drawLine(x, rect.top(), x, rect.bottom())

            if self.h_grid_enabled:
                for y in range(top, bottom, self.grid_size):
                    painter.drawLine(rect.left(), y, rect.right(), y)

    def snap_to_grid(self, point, **kwargs):
        x, y = point.x(), point.y()
        if self.v_grid_enabled:
            x = round(x / self.grid_size) * self.grid_size
        if self.h_grid_enabled:
            if kwargs.get("bol", False):
                y = round((y) / self.grid_size) * self.grid_size
            else:
                y = round((y + self.rect_height) / self.grid_size) * self.grid_size - self.rect_height

        # y = round(y / self.grid_size) * self.grid_size
        return QPointF(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.right_button_pressed = True
            self.delete_under_cursor(event.scenePos())
        elif event.button() == Qt.MouseButton.LeftButton:
            if not self.itemAt(event.scenePos(), QTransform()):
                self.drawing = True
                self.start_point = self.snap_to_grid(event.scenePos()) if (
                        self.v_grid_enabled or self.h_grid_enabled) else event.scenePos()
                self.current_rect = RectangleItem(QRectF(
                    self.start_point.x(),
                    self.start_point.y(),
                    0,
                    self.rect_height
                ))
                self.addItem(self.current_rect)
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.right_button_pressed:
            self.delete_under_cursor(event.scenePos())
        elif self.drawing and self.current_rect:
            end_point = self.snap_to_grid(event.scenePos()) if (
                    self.v_grid_enabled or self.h_grid_enabled) else event.scenePos()

            # Создаем прямоугольник в любом направлении
            if end_point.x() < self.start_point.x():
                self.current_rect.setRect(
                    end_point.x(),
                    self.start_point.y(),
                    self.start_point.x() - end_point.x(),
                    self.rect_height
                )
            else:
                self.current_rect.setRect(
                    self.start_point.x(),
                    self.start_point.y(),
                    end_point.x() - self.start_point.x(),
                    self.rect_height
                )

            if self.views():
                self.views()[0].viewport().update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.right_button_pressed = False
        elif self.drawing and self.current_rect:
            self.drawing = False
            if abs(self.current_rect.rect().width()) < 5:
                self.removeItem(self.current_rect)
            self.current_rect = None

        super().mouseReleaseEvent(event)

    def delete_under_cursor(self, pos):
        """Удаляет все прямоугольники под курсором"""
        items = self.items(pos)
        for item in items:
            if isinstance(item, RectangleItem):
                item.fade_out_and_remove()
                # self.removeItem(item)
        if items:
            self.update()


# ... (остальные классы InfiniteView и RectangleEditor остаются без изменений)
class InfiniteView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setInteractive(True)
        self.scale(1.5, 1.5)

        self.x_scale = 1.0
        self.y_scale = 1.0
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

    def apply_scaling(self):
        transform = QTransform()
        transform.scale(self.x_scale, self.y_scale)
        self.setTransform(transform)


class RectangleEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Редактор с привязкой к сетке")
        self.resize(800, 600)

        self.scene = InfiniteScene()
        self.view = InfiniteView(self.scene)

        self.x_scale_slider = ScaleSlider(Qt.Orientation.Horizontal)
        self.x_scale_slider.setMinimumWidth(200)
        self.x_scale_slider.valueChanged.connect(self.update_x_scale)
        self.x_scale_slider.sliderWheelMoved.connect(self.handle_slider_wheel)

        self.y_scale_slider = ScaleSlider(Qt.Orientation.Vertical)
        self.y_scale_slider.setMinimumHeight(200)
        self.y_scale_slider.valueChanged.connect(self.update_y_scale)
        self.y_scale_slider.sliderWheelMoved.connect(self.handle_slider_wheel)

        x_label = QLabel("Масштаб X:")
        y_label = QLabel("Масштаб Y:")
        y_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.h_grid_check = QCheckBox("Горизонтальная сетка")
        self.h_grid_check.setChecked(True)
        self.h_grid_check.stateChanged.connect(self.toggle_h_grid)

        self.v_grid_check = QCheckBox("Вертикальная сетка")
        self.v_grid_check.setChecked(True)
        self.v_grid_check.stateChanged.connect(self.toggle_v_grid)

        self.toolbar = QHBoxLayout()
        self.toolbar.addWidget(x_label)
        self.toolbar.addWidget(self.x_scale_slider)
        self.toolbar.addWidget(self.h_grid_check)
        self.toolbar.addWidget(self.v_grid_check)
        self.toolbar.addStretch()

        y_slider_container = QWidget()
        y_slider_layout = QVBoxLayout(y_slider_container)
        y_slider_layout.addWidget(y_label)
        y_slider_layout.addWidget(self.y_scale_slider)
        y_slider_layout.addStretch()

        main_layout = QHBoxLayout()

        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.addLayout(self.toolbar)
        left_layout.addWidget(self.view)

        main_layout.addWidget(left_container)
        main_layout.addWidget(y_slider_container)

        self.setLayout(main_layout)

        self.update_x_scale(100)
        self.update_y_scale(100)

    def update_x_scale(self, value):
        scale = value / 100.0
        self.view.x_scale = scale
        self.view.apply_scaling()

    def update_y_scale(self, value):
        scale = value / 100.0
        self.view.y_scale = scale
        self.view.apply_scaling()

    def handle_slider_wheel(self, delta):
        slider = self.sender()
        if delta > 0:
            slider.setValue(slider.value() + slider.singleStep())
        else:
            slider.setValue(slider.value() - slider.singleStep())

    def toggle_h_grid(self, state):
        self.scene.h_grid_enabled = state == Qt.CheckState.Checked.value
        self.scene.update()

    def toggle_v_grid(self, state):
        self.scene.v_grid_enabled = state == Qt.CheckState.Checked.value
        self.scene.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = RectangleEditor()
    editor.show()
    sys.exit(app.exec())