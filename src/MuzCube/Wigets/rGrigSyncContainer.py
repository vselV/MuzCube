import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout,
                             QGraphicsView, QGraphicsScene, QLabel, QPushButton,
                             QTextEdit, QFrame, QSpinBox, QComboBox, QVBoxLayout, QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QWheelEvent


class SyncManager(QObject):
    """Менеджер синхронизации для графических сцен"""
    sync_horizontal_scroll = pyqtSignal(int)
    sync_vertical_scroll = pyqtSignal(int)
    sync_horizontal_scale = pyqtSignal(float)
    sync_vertical_scale = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.connected_views = []


class SynchronizableGraphicsView(QGraphicsView):
    """Расширенный QGraphicsView с поддержкой синхронизации"""

    def __init__(self, scene, sync_manager, view_id):
        super().__init__(scene)
        self.sync_manager = sync_manager
        self.view_id = view_id
        self.setup_connections()

    def setup_connections(self):
        """Настраивает соединения для синхронизации"""
        self.sync_manager.sync_horizontal_scroll.connect(self.on_horizontal_scroll_sync)
        self.sync_manager.sync_vertical_scroll.connect(self.on_vertical_scroll_sync)
        self.sync_manager.sync_horizontal_scale.connect(self.on_horizontal_scale_sync)
        self.sync_manager.sync_vertical_scale.connect(self.on_vertical_scale_sync)

    def on_horizontal_scroll_sync(self, value):
        """Синхронизация горизонтальной прокрутки"""
        if self.sender() != self:
            self.horizontalScrollBar().setValue(value)

    def on_vertical_scroll_sync(self, value):
        """Синхронизация вертикальной прокрутки"""
        if self.sender() != self:
            self.verticalScrollBar().setValue(value)

    def on_horizontal_scale_sync(self, scale):
        """Синхронизация горизонтального масштаба"""
        if self.sender() != self:
            transform = self.transform()
            transform.setMatrix(scale, transform.m12(), transform.m13(),
                                transform.m21(), transform.m22(), transform.m23(),
                                transform.m31(), transform.m32(), transform.m33())
            self.setTransform(transform)

    def on_vertical_scale_sync(self, scale):
        """Синхронизация вертикального масштаба"""
        if self.sender() != self:
            transform = self.transform()
            transform.setMatrix(transform.m11(), transform.m12(), transform.m13(),
                                transform.m21(), scale, transform.m23(),
                                transform.m31(), transform.m32(), transform.m33())
            self.setTransform(transform)

    def wheelEvent(self, event: QWheelEvent):
        """Обработка колесика мыши для масштабирования"""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Масштабирование с Ctrl
            zoom_factor = 1.15
            if event.angleDelta().y() < 0:
                zoom_factor = 1.0 / zoom_factor

            self.scale(zoom_factor, zoom_factor)
            self.sync_manager.sync_horizontal_scale.emit(self.transform().m11())
            self.sync_manager.sync_vertical_scale.emit(self.transform().m22())
            event.accept()
        else:
            super().wheelEvent(event)

    def scrollContentsBy(self, dx, dy):
        """Перехват прокрутки для синхронизации"""
        super().scrollContentsBy(dx, dy)

        # Отправляем сигналы синхронизации
        self.sync_manager.sync_horizontal_scroll.emit(self.horizontalScrollBar().value())
        self.sync_manager.sync_vertical_scroll.emit(self.verticalScrollBar().value())


class AdvancedSeamlessContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_layout = QGridLayout(self)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(0)
        self.widgets = {}
        self.graphics_views = {}  # Специальный словарь для графических видов
        self.sync_managers = {
            'horizontal_scroll': SyncManager(),
            'vertical_scroll': SyncManager(),
            'horizontal_scale': SyncManager(),
            'vertical_scale': SyncManager()
        }

    def add_to_grid(self, widget, row, column, row_span=1, column_span=1):
        """Базовый метод добавления виджета в сетку"""
        self.grid_layout.addWidget(widget, row, column, row_span, column_span)

        if isinstance(widget, (QGraphicsView, QFrame)):
            widget.setFrameShape(QFrame.Shape.NoFrame)

       # if isinstance(widget, QGraphicsView):
          #  widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
           # widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        key = f"{row}_{column}"
        self.widgets[key] = widget
        return widget
    def add_scene(self, scene, row, column, row_span=1, column_span=1):
        view_id = f"{row}_{column}"
        view = SynchronizableGraphicsView(scene, self.sync_managers['horizontal_scroll'], view_id)
        self.graphics_views[view_id] = view
        self.add_to_grid(view, row, column, row_span, column_span)
        return view
    def add_graphics_scene(self, row, column, row_span=1, column_span=1, bg_color=Qt.GlobalColor.white):
        """Создает и добавляет синхронизируемую графическую сцену"""
        scene = QGraphicsScene()
        scene.setSceneRect(-10000, -10000, 20000, 20000)
        scene.setBackgroundBrush(bg_color)

        # Добавляем тестовый контент
        rect = scene.addRect(0, 0, 500, 300)
        rect.setBrush(bg_color)
        text = scene.addText(f"Сцена {row}-{column}")
        text.setPos(200, 130)

        view_id = f"{row}_{column}"
        view = SynchronizableGraphicsView(scene, self.sync_managers['horizontal_scroll'], view_id)

        # Сохраняем ссылку на графический вид
        self.graphics_views[view_id] = view

        return self.add_to_grid(view, row, column, row_span, column_span), scene

    def sync_scenes(self, source_cell, target_cell, sync_type):
        """
        Синхронизирует параметры между сценами

        Аргументы:
        source_cell - кортеж (row, column) исходной сцены
        target_cell - кортеж (row, column) целевой сцены
        sync_type - тип синхронизации:
                   'horizontal_scroll', 'vertical_scroll',
                   'horizontal_scale', 'vertical_scale'
        """
        source_id = f"{source_cell[0]}_{source_cell[1]}"
        target_id = f"{target_cell[0]}_{target_cell[1]}"

        if source_id not in self.graphics_views or target_id not in self.graphics_views:
            print(f"Ошибка: одна из сцен не найдена ({source_id} -> {target_id})")
            return False

        source_view = self.graphics_views[source_id]
        target_view = self.graphics_views[target_id]

        # Подключаем к соответствующему менеджеру синхронизации
        sync_manager = self.sync_managers[sync_type]

        # Отключаем предыдущие соединения (если были)
        try:
            if sync_type == 'horizontal_scroll':
                sync_manager.sync_horizontal_scroll.disconnect()
            elif sync_type == 'vertical_scroll':
                sync_manager.sync_vertical_scroll.disconnect()
            elif sync_type == 'horizontal_scale':
                sync_manager.sync_horizontal_scale.disconnect()
            elif sync_type == 'vertical_scale':
                sync_manager.sync_vertical_scale.disconnect()
        except:
            pass  # Если не было соединений - игнорируем

        # Устанавливаем начальное значение
        if sync_type == 'horizontal_scroll':
            target_view.horizontalScrollBar().setValue(
                source_view.horizontalScrollBar().value()
            )
        elif sync_type == 'vertical_scroll':
            target_view.verticalScrollBar().setValue(
                source_view.verticalScrollBar().value()
            )
        elif sync_type == 'horizontal_scale':
            target_view.scale(
                source_view.transform().m11() / target_view.transform().m11(),
                1.0
            )
        elif sync_type == 'vertical_scale':
            target_view.scale(
                1.0,
                source_view.transform().m22() / target_view.transform().m22()
            )

        print(f"Синхронизировано {source_id} -> {target_id} ({sync_type})")
        return True

    def sync_all_scenes(self, sync_type):
        """Синхронизирует все сцены по указанному параметру"""
        if not self.graphics_views:
            return

        # Берем первую сцену как источник
        source_id = list(self.graphics_views.keys())[0]
        source_view = self.graphics_views[source_id]

        for target_id, target_view in self.graphics_views.items():
            if target_id != source_id:
                if sync_type == 'horizontal_scroll':
                    target_view.horizontalScrollBar().setValue(
                        source_view.horizontalScrollBar().value()
                    )
                elif sync_type == 'vertical_scroll':
                    target_view.verticalScrollBar().setValue(
                        source_view.verticalScrollBar().value()
                    )
                elif sync_type == 'horizontal_scale':
                    target_view.scale(
                        source_view.transform().m11() / target_view.transform().m11(),
                        1.0
                    )
                elif sync_type == 'vertical_scale':
                    target_view.scale(
                        1.0,
                        source_view.transform().m22() / target_view.transform().m22()
                    )

    # Остальные методы остаются без изменений
    def add_label(self, text, row, column, row_span=1, column_span=1, **kwargs):
        label = QLabel(text)
        label.setAlignment(kwargs.get('alignment', Qt.AlignmentFlag.AlignCenter))
        if 'style' in kwargs:
            label.setStyleSheet(kwargs['style'])
        return self.add_to_grid(label, row, column, row_span, column_span)

    def add_button(self, text, row, column, row_span=1, column_span=1, callback=None):
        button = QPushButton(text)
        if callback:
            button.clicked.connect(callback)
        return self.add_to_grid(button, row, column, row_span, column_span)

    def set_stretch(self, rows=None, columns=None):
        if rows:
            for row, stretch in rows.items():
                self.grid_layout.setRowStretch(row, stretch)
        if columns:
            for col, stretch in columns.items():
                self.grid_layout.setColumnStretch(col, stretch)


class SyncExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Синхронизированные бесшовные сцены")
        self.setGeometry(100, 100, 1400, 800)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Создаем контейнер с сценами
        self.container = AdvancedSeamlessContainer()
        main_layout.addWidget(self.container, 4)  # 4/5 места для сцен

        # Панель управления синхронизацией
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        main_layout.addWidget(control_panel, 1)  # 1/5 места для управления

        # Кнопки синхронизации
        sync_types = ['horizontal_scroll', 'vertical_scroll', 'horizontal_scale', 'vertical_scale']
        sync_names = ['Гориз. прокрутка', 'Верт. прокрутка', 'Гориз. масштаб', 'Верт. масштаб']

        for sync_type, name in zip(sync_types, sync_names):
            btn = QPushButton(f"Синхр. все: {name}")
            btn.clicked.connect(lambda checked, st=sync_type: self.container.sync_all_scenes(st))
            control_layout.addWidget(btn)

        # Кнопки индивидуальной синхронизации
        individual_btn = QPushButton("Синхр. (0,0)->(0,1): Гориз. прокрутка")
        individual_btn.clicked.connect(lambda: self.container.sync_scenes((0, 0), (0, 1), 'horizontal_scroll'))
        control_layout.addWidget(individual_btn)

        individual_btn2 = QPushButton("Синхр. (0,0)->(1,0): Верт. прокрутка")
        individual_btn2.clicked.connect(lambda: self.container.sync_scenes((0, 0), (1, 0), 'vertical_scroll'))
        control_layout.addWidget(individual_btn2)

        # Создаем сетку сцен
        self.setup_scenes()

    def setup_scenes(self):
        """Создает сетку из 4 сцен"""
        # Первая строка
        self.container.add_graphics_scene(0, 0, bg_color=Qt.GlobalColor.blue)
        self.container.add_graphics_scene(0, 1, bg_color=Qt.GlobalColor.red)

        # Вторая строка
        self.container.add_graphics_scene(1, 0, bg_color=Qt.GlobalColor.green)
        self.container.add_graphics_scene(1, 1, bg_color=Qt.GlobalColor.yellow)

        # Настраиваем растяжение
        self.container.set_stretch(
            rows={0: 1, 1: 1},
            columns={0: 1, 1: 1}
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SyncExample()
    window.show()
    sys.exit(app.exec())