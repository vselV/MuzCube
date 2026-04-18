import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QSplitter, QGridLayout, QTextEdit, QFrame,
                             QVBoxLayout, QHBoxLayout, QLabel, QPushButton)
from PyQt6.QtCore import Qt


class SynchronizedSplitterGrid():
    def __init__(self, splitter:QSplitter=None, grid_layout=None, parent=None):
        #super().__init__(parent)
        self.splitter = splitter
        self.grid_layout = grid_layout
        self.grid_widget = None

        #self.initUI()
        self.my_initUI()
    def my_initUI(self):
        self.splitter.splitterMoved.connect(self.update_grid_from_splitter)
    def initUI(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Если grid_layout передан, создаем для него контейнер
        if self.grid_layout:
            self.grid_widget = QWidget()
            self.grid_widget.setLayout(self.grid_layout)
            main_layout.addWidget(self.grid_widget, 3)  # Grid занимает 3/4

        # Если splitter передан, добавляем его
        if self.splitter:
            # Настраиваем splitter если он еще не настроен
            if self.splitter.handleWidth() == 0:
                self.splitter.setHandleWidth(8)
            if not self.splitter.styleSheet():
                self.splitter.setStyleSheet("QSplitter::handle { background-color: #cccccc; }")

            main_layout.addWidget(self.splitter, 1)  # Splitter занимает 1/4

        # Синхронизируем если оба элемента переданы
        if self.splitter and self.grid_layout:
            self.synchronize_layouts()
    def add_sync_widget(self,widget1,widget2):
        self.splitter.addWidget(widget2)
        self.grid_layout.addWidget(widget1,self.splitter.count(),0)
        #self.splitter.splitterMoved.emit(0,self.splitter.count()-1)
        self.update_grid_from_splitter()

    def synchronize_layouts(self):
        """Синхронизирует Grid Layout с Splitter"""
        # Проверяем соответствие количества элементов
        splitter_count = self.splitter.count()
        grid_row_count = self.get_grid_row_count()

        if splitter_count != grid_row_count:
            print(f"Warning: Splitter has {splitter_count} elements, Grid has {grid_row_count} rows")
            return

        # Подключаем синхронизацию
        self.splitter.splitterMoved.connect(self.update_grid_from_splitter)

        # Первоначальная синхронизация
        self.update_grid_from_splitter()


    def get_grid_row_count(self):
        """Возвращает количество строк в Grid Layout"""
        if not self.grid_layout:
            return 0

        count = 0
        for i in range(self.grid_layout.rowCount()):
            # Проверяем есть ли хотя бы один элемент в строке
            for j in range(self.grid_layout.columnCount()):
                item = self.grid_layout.itemAtPosition(i, j)
                if item and item.widget():
                    count = i + 1
                    break
        return count

    def update_grid_from_splitter(self, pos=None, index=None):
        """Обновляет Grid Layout согласно текущим размерам Splitter"""
        if not self.splitter or not self.grid_layout:
            return

        sizes = self.splitter.sizes()
        if not sizes or sum(sizes) == 0:
            return

        # Обновляем stretch factors для строк Grid Layout
        for i, size in enumerate(sizes):
            if i < self.grid_layout.rowCount():
                self.grid_layout.setRowStretch(i, size)

        # Принудительное обновление layout
        self.grid_layout.update()


# Пример использования с готовыми компонентами
def create_example_components():
    """Создает пример готовых компонентов для демонстрации"""

    # Создаем и настраиваем Splitter
    splitter = QSplitter(Qt.Orientation.Vertical)
    for i in range(4):
        widget = QTextEdit(f"Splitter Widget {i + 1}")
        widget.setMinimumHeight(50)
        splitter.addWidget(widget)

    # Создаем и настраиваем Grid Layout
    grid_layout = QGridLayout()
    grid_layout.setSpacing(5)
    grid_layout.setContentsMargins(5, 5, 5, 5)

    for i in range(4):
        widget = QTextEdit(f"Grid Widget {i + 1}")
        widget.setMinimumHeight(50)
        grid_layout.addWidget(widget, i, 0)

    return splitter, grid_layout


class DemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Synchronized Ready Components")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Создаем готовые компоненты
        splitter, grid_layout = create_example_components()

        # Создаем синхронизированный виджет
        self.sync_widget = SynchronizedSplitterGrid(splitter, grid_layout)

        # Добавляем кнопки для управления
        control_layout = QHBoxLayout()

        btn_add_splitter = QPushButton("Добавить элемент в Splitter")
        btn_add_splitter.clicked.connect(self.add_to_splitter)
        control_layout.addWidget(btn_add_splitter)

        btn_add_grid = QPushButton("Добавить элемент в Grid")
        btn_add_grid.clicked.connect(self.add_to_grid)
        control_layout.addWidget(btn_add_grid)

        btn_reset = QPushButton("Сбросить синхронизацию")
        btn_reset.clicked.connect(self.reset_synchronization)
        control_layout.addWidget(btn_reset)

        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.sync_widget, 1)

        self.setCentralWidget(central_widget)

    def add_to_splitter(self):
        """Добавляет новый элемент в splitter"""
        if self.sync_widget.splitter:
            new_widget = QTextEdit(f"New Splitter {self.sync_widget.splitter.count() + 1}")
            new_widget.setMinimumHeight(50)
            self.sync_widget.splitter.addWidget(new_widget)

            # Пересинхронизируем
            self.sync_widget.synchronize_layouts()

    def add_to_grid(self):
        """Добавляет новый элемент в grid layout"""
        if self.sync_widget.grid_layout:
            row_count = self.sync_widget.get_grid_row_count()
            new_widget = QTextEdit(f"New Grid {row_count + 1}")
            new_widget.setMinimumHeight(50)
            self.sync_widget.grid_layout.addWidget(new_widget, row_count, 0)

            # Пересинхронизируем
            self.sync_widget.synchronize_layouts()

    def reset_synchronization(self):
        """Сбрасывает и заново устанавливает синхронизацию"""
        if self.sync_widget.splitter:
            # Отключаем старые соединения
            try:
                self.sync_widget.splitter.splitterMoved.disconnect()
            except:
                pass

            # Устанавливаем заново
            self.sync_widget.synchronize_layouts()


# Альтернативный конструктор для удобства
class SynchronizedContainer:
    @staticmethod
    def create_from_components(splitter, grid_layout, parent=None):
        """Создает синхронизированный контейнер из готовых компонентов"""
        return SynchronizedSplitterGrid(splitter, grid_layout, parent)

    @staticmethod
    def create_empty(parent=None):
        """Создает пустой контейнер для последующего добавления компонентов"""
        return SynchronizedSplitterGrid(None, None, parent)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Способ 1: Создание с готовыми компонентами
    splitter, grid_layout = create_example_components()
    window = DemoWindow()

    # Способ 2: Постепенное добавление компонентов
    # sync_container = SynchronizedContainer.create_empty()
    # sync_container.splitter = splitter
    # sync_container.grid_layout = grid_layout
    # sync_container.initUI()  # Переинициализируем

    window.show()
    sys.exit(app.exec())