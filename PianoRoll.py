import sys
from dataclasses import dataclass
from PyQt6.QtCore import Qt, QRectF, QPointF, QLineF, QTimer
from PyQt6.QtGui import (QPainter, QColor, QPen, QBrush, QFont, QMouseEvent,
                         QKeyEvent, QTransform)
from PyQt6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene,
                            QGraphicsItem, QVBoxLayout, QHBoxLayout,
                            QWidget, QPushButton, QCheckBox, QSpinBox,
                            QLabel, QScrollBar)


@dataclass
class Note:
    start_time: float  # Время начала в тиках (1 четверть = 960 тиков)
    channel: int  # MIDI канал (0-15)
    pitch: int  # Высота ноты (0-127)
    velocity: int  # Громкость ноты (1-127)
    pitch_wheel: int  # Значение pitch wheel (-8192 до 8191)
    duration: float  # Длительность в тиках


class PianoRollNote(QGraphicsItem):
    def __init__(self, note: Note, parent=None):
        super().__init__(parent)
        self.note = note
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.color = QColor(0, 120, 215)  # Синий цвет по умолчанию
        self.hover_color = QColor(0, 150, 255)
        self.selected_color = QColor(255, 100, 0)
        self.is_hovered = False
        self.is_resizing = False
        self.resize_handle_size = 8
        self.min_width = 10
        self.min_height = 10

    def boundingRect(self):
        return QRectF(0, 0, self.note.duration, 1)

    def paint(self, painter, option, widget):
        # Определяем цвет в зависимости от состояния
        if self.isSelected():
            color = self.selected_color
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.color

        # Рисуем основную часть ноты
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(Qt.GlobalColor.black, 0.5))
        painter.drawRect(0, 0, self.note.duration, 1)

        # Рисуем ручку для изменения длины
        if self.isSelected() or self.is_hovered:
            resize_handle = QRectF(
                self.note.duration - self.resize_handle_size / 2,
                0.5 - self.resize_handle_size / 2,
                self.resize_handle_size,
                self.resize_handle_size
            )
            painter.setBrush(QBrush(Qt.GlobalColor.white))
            painter.drawEllipse(resize_handle)

    def mousePressEvent(self, event):
        # Проверяем, нажали ли на ручку изменения размера
        resize_handle = QRectF(
            self.note.duration - self.resize_handle_size / 2,
            0.5 - self.resize_handle_size / 2,
            self.resize_handle_size,
            self.resize_handle_size
        )

        if resize_handle.contains(event.pos()):
            self.is_resizing = True
        else:
            self.is_resizing = False
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_resizing:
            # Изменяем длительность ноты
            new_duration = max(self.min_width, event.pos().x())
            if hasattr(self.scene(), 'snap_enabled') and self.scene().snap_enabled:
                new_duration = self.scene().snap_to_grid(new_duration)
            self.note.duration = new_duration
            self.prepareGeometryChange()
        else:
            # Перемещаем ноту
            super().mouseMoveEvent(event)
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                # Только по горизонтали при зажатом Shift
                new_pos = QPointF(event.scenePos().x(), self.pos().y())
                self.setPos(new_pos)
            elif event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                # Только по вертикали при зажатом Ctrl
                new_pos = QPointF(self.pos().x(), event.scenePos().y())
                self.setPos(new_pos)

            # Обновляем параметры ноты
            if hasattr(self.scene(), 'snap_enabled') and self.scene().snap_enabled:
                snapped_pos = self.scene().snap_to_grid(self.pos().x())
                self.setX(snapped_pos)

            self.note.start_time = self.pos().x()
            self.note.pitch = 127 - int(self.pos().y())

    def hoverEnterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().hoverLeaveEvent(event)


class PianoRollScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.snap_enabled = True
        self.grid_size = 960 / 4  # 1/16 ноты (960 тиков / 4 = 240 тиков)
        self.playhead_pos = 0
        self.playhead = self.addLine(0, 0, 0, 127, QPen(Qt.GlobalColor.red, 2))
        self.playhead.setZValue(1000)  # Чтобы был поверх всех элементов

        # Настройки внешнего вида
        self.setBackgroundBrush(QBrush(QColor(40, 40, 40)))
        self.note_color = QColor(0, 120, 215)

        # Создаем тестовые данные
        self.create_test_data()

    def create_test_data(self):
        # Тестовые ноты для демонстрации
        notes = [
            Note(0, 0, 60, 100, 0, 960),  # C4, длительность 1 четверть
            Note(960, 0, 64, 100, 0, 960),  # E4
            Note(1920, 0, 67, 100, 0, 960),  # G4
            Note(2880, 0, 60, 100, 0, 960),  # C4
        ]

        for note in notes:
            self.add_note(note)

    def add_note(self, note):
        note_item = PianoRollNote(note)
        note_item.setPos(note.start_time, 127 - note.pitch)
        self.addItem(note_item)
        return note_item

    def snap_to_grid(self, value):
        return round(value / self.grid_size) * self.grid_size

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        # Рисуем вертикальную сетку
        pen = QPen(QColor(80, 80, 80), 0.5)
        painter.setPen(pen)

        left = int(rect.left()) - (int(rect.left()) % int(self.grid_size))
        right = int(rect.right())

        for x in range(left, right, int(self.grid_size)):
            painter.drawLine(x, rect.top(), x, rect.bottom())

        # Рисуем горизонтальную сетку (клавиши пианино)
        for y in range(0, 128):
            if y % 12 in [0, 2, 4, 5, 7, 9, 11]:  # Белые клавиши
                painter.setPen(QPen(QColor(100, 100, 100), 0.5))
            else:  # Черные клавиши
                painter.setPen(QPen(QColor(60, 60, 60), 0.5))

            painter.drawLine(rect.left(), y, rect.right(), y)

    def update_playhead(self, pos):
        self.playhead_pos = pos
        self.playhead.setLine(pos, 0, pos, 127)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Если клик не на элементе, создаем новую ноту
            if not self.itemAt(event.scenePos(), QTransform()):
                pos = event.scenePos()
                if self.snap_enabled:
                    pos.setX(self.snap_to_grid(pos.x()))

                # Создаем новую ноту
                new_note = Note(
                    start_time=pos.x(),
                    channel=0,
                    pitch=127 - int(pos.y()),
                    velocity=100,
                    pitch_wheel=0,
                    duration=self.grid_size * 2  # 1/8 ноты по умолчанию
                )
                self.add_note(new_note)
                return

        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        # Удаление выбранных нот по нажатию Delete
        if event.key() == Qt.Key.Key_Delete:
            for item in self.selectedItems():
                if isinstance(item, PianoRollNote):
                    self.removeItem(item)
        else:
            super().keyPressEvent(event)


class PianoRollView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        # Настройки масштабирования
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Для плавной прокрутки
        self.setInteractive(True)

    def wheelEvent(self, event):
        # Масштабирование при Ctrl + колесо мыши
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            zoom_factor = 1.15
            if event.angleDelta().y() < 0:
                zoom_factor = 1 / zoom_factor
            self.scale(zoom_factor, zoom_factor)
        else:
            # Обычная прокрутка
            super().wheelEvent(event)


class PianoRollEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("MIDI Piano Roll Editor")
        self.resize(1000, 600)

        # Создаем сцену и представление
        self.scene = PianoRollScene()
        self.view = PianoRollView(self.scene)

        # Панель инструментов
        self.toolbar = QHBoxLayout()

        self.snap_checkbox = QCheckBox("Привязка к сетке")
        self.snap_checkbox.setChecked(True)
        self.snap_checkbox.stateChanged.connect(self.toggle_snap)

        self.grid_size_spin = QSpinBox()
        self.grid_size_spin.setRange(1, 16)
        self.grid_size_spin.setValue(4)
        self.grid_size_spin.setPrefix("1/")
        self.grid_size_spin.valueChanged.connect(self.update_grid_size)

        self.playhead_label = QLabel("Позиция: 0")

        self.toolbar.addWidget(self.snap_checkbox)
        self.toolbar.addWidget(QLabel("Размер сетки:"))
        self.toolbar.addWidget(self.grid_size_spin)
        self.toolbar.addStretch()
        self.toolbar.addWidget(self.playhead_label)

        # Главный лэйаут
        layout = QVBoxLayout()
        layout.addLayout(self.toolbar)
        layout.addWidget(self.view)

        self.setLayout(layout)

        # Таймер для обновления позиции проигрывания
        self.playhead_timer = QTimer()
        self.playhead_timer.timeout.connect(self.update_playhead)
        self.playhead_timer.start(50)  # 20 FPS

    def toggle_snap(self, state):
        self.scene.snap_enabled = state == Qt.CheckState.Checked.value

    def update_grid_size(self, value):
        self.scene.grid_size = 960 / value
        self.scene.update()

    def update_playhead(self):
        # В реальном приложении здесь нужно получать позицию из MIDI плеера
        # Для демонстрации просто двигаем вперед и сбрасываем в 0
        current_pos = self.scene.playhead_pos + 10
        if current_pos > 5000:
            current_pos = 0
        self.scene.update_playhead(current_pos)
        self.playhead_label.setText(f"Позиция: {current_pos}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = PianoRollEditor()
    editor.show()
    sys.exit(app.exec())