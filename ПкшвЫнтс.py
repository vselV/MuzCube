import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QSplitter, QGridLayout, QTextEdit, QFrame,
                             QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer


class PerfectSynchronizedLayout(QWidget):
    def __init__(self, num_elements=4):
        super().__init__()
        self.num_elements = num_elements
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Grid Layout слева
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        # Splitter справа
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setContentsMargins(0, 0, 0, 0)
        self.splitter.setHandleWidth(8)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #cccccc;
                height: 8px;
            }
        """)

        # Создаем элементы
        self.grid_elements = []
        self.splitter_elements = []

        for i in range(self.num_elements):
            # Для Grid Layout
            grid_element = QTextEdit(f"Grid Item {i + 1}")
            grid_element.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.grid_layout.addWidget(grid_element, i, 0)
            self.grid_elements.append(grid_element)

            # Для Splitter
            splitter_element = QTextEdit(f"Splitter Item {i + 1}")
            self.splitter.addWidget(splitter_element)
            self.splitter_elements.append(splitter_element)

        # Добавляем разделители в Grid
        for i in range(self.num_elements - 1):
            divider = QFrame()
            divider.setFrameShape(QFrame.Shape.HLine)
            divider.setFrameShadow(QFrame.Shadow.Sunken)
            divider.setFixedHeight(8)
            divider.setStyleSheet("background-color: #cccccc;")
            self.grid_layout.addWidget(divider, i, 1)

        # Настраиваем stretch factors
        for i in range(self.num_elements):
            self.grid_layout.setRowStretch(i, 1)

        # Добавляем в основной layout
        main_layout.addWidget(self.grid_container, 2)
        main_layout.addWidget(self.splitter, 1)

        # Синхронизация
        self.splitter.splitterMoved.connect(self.on_splitter_moved)
        QTimer.singleShot(50, self.initial_sync)

    def initial_sync(self):
        """Первоначальная синхронизация"""
        self.update_grid_from_splitter()

    def on_splitter_moved(self, pos, index):
        """Обработчик перемещения splitter"""
        self.update_grid_from_splitter()

    def update_grid_from_splitter(self):
        """Обновляет Grid Layout согласно текущим размерам Splitter"""
        sizes = self.splitter.sizes()
        if not sizes or sum(sizes) == 0:
            return

        total_height = self.splitter.height()

        # Обновляем stretch factors
        for i, size in enumerate(sizes):
            if i < self.num_elements:
                # Устанавливаем stretch factor пропорционально размеру
                self.grid_layout.setRowStretch(i, size)

                # Обновляем минимальную высоту для визуального соответствия
                self.grid_elements[i].setMinimumHeight(max(30, size))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Perfect Synchronization: Splitter ↔ Grid")
        self.setGeometry(100, 100, 1400, 900)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Заголовок
        title = QLabel("Синхронизированный Splitter и Grid Layout")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Основной виджет
        self.sync_layout = PerfectSynchronizedLayout(6)  # 6 элементов
        layout.addWidget(self.sync_layout, 1)

        # Информация
        info = QLabel(
            "• Перетаскивайте разделители в правой части\n• Левая сетка автоматически синхронизируется\n• Границы всегда совпадают")
        info.setStyleSheet("color: #666; padding: 10px;")
        layout.addWidget(info)

        self.setCentralWidget(central_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())