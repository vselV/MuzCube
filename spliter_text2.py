import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QSplitter, QTextEdit, QSplitterHandle,
                             QCheckBox, QVBoxLayout, QHBoxLayout, QLabel)
from PyQt6.QtCore import Qt


class ExcelGrid(QWidget):
    def __init__(self, rows=3, cols=3):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.horizontal_splitters = {}  # {(row, col): splitter}
        self.vertical_splitters = {}  # {col: splitter}
        self.cells = {}  # {(row, col): widget}
        self.locked_horizontal = set()  # Заблокированные горизонтальные
        self.locked_vertical = set()  # Заблокированные вертикальные
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Создаем строки
        for i in range(self.rows):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setSpacing(0)
            row_layout.setContentsMargins(0, 0, 0, 0)

            for j in range(self.cols):
                # Создаем ячейку
                cell = QTextEdit(f"Row {i + 1}, Col {j + 1}")
                cell.setMinimumSize(50, 30)
                self.cells[(i, j)] = cell
                row_layout.addWidget(cell)

                # Добавляем вертикальный разделитель (кроме последней колонки)
                if j < self.cols - 1:
                    vsplitter = QSplitter(Qt.Orientation.Vertical)
                    vsplitter.setChildrenCollapsible(False)
                    vsplitter.setHandleWidth(8)
                    vsplitter.setStyleSheet("QSplitter::handle { background-color: #cccccc; }")
                    self.vertical_splitters[j] = vsplitter
                    row_layout.addWidget(vsplitter)

            main_layout.addWidget(row_widget)

            # Добавляем горизонтальный разделитель (кроме последней строки)
            if i < self.rows - 1:
                hsplitter = QSplitter(Qt.Orientation.Horizontal)
                hsplitter.setChildrenCollapsible(False)
                hsplitter.setHandleWidth(8)
                hsplitter.setStyleSheet("QSplitter::handle { background-color: #cccccc; }")
                self.horizontal_splitters[(i, j)] = hsplitter  # Сохраняем для каждой колонки
                main_layout.addWidget(hsplitter)

        # Синхронизируем разделители
        self.syncSplitters()

    def syncSplitters(self):
        """Синхронизирует все разделители"""
        # Синхронизация вертикальных разделителей
        if self.vertical_splitters:
            master_vsplitter = list(self.vertical_splitters.values())[0]

            def sync_vertical(pos, index):
                for vsplitter in self.vertical_splitters.values():
                    if vsplitter != master_vsplitter and id(vsplitter) not in self.locked_vertical:
                        vsplitter.blockSignals(True)
                        vsplitter.moveSplitter(pos, index)
                        vsplitter.blockSignals(False)

            master_vsplitter.splitterMoved.connect(sync_vertical)

        # Синхронизация горизонтальных разделителей
        if self.horizontal_splitters:
            master_hsplitter = list(self.horizontal_splitters.values())[0]

            def sync_horizontal(pos, index):
                for hsplitter in self.horizontal_splitters.values():
                    if hsplitter != master_hsplitter and id(hsplitter) not in self.locked_horizontal:
                        hsplitter.blockSignals(True)
                        hsplitter.moveSplitter(pos, index)
                        hsplitter.blockSignals(False)

            master_hsplitter.splitterMoved.connect(sync_horizontal)

    def setHorizontalSplitterVisible(self, row, col, visible):
        """Устанавливает видимость горизонтального разделителя"""
        key = (row, col)
        if key in self.horizontal_splitters:
            splitter = self.horizontal_splitters[key]
            if visible:
                splitter.show()
                splitter.setHandleWidth(8)
                self.locked_horizontal.discard(id(splitter))
            else:
                splitter.hide()
                splitter.setHandleWidth(0)
                self.locked_horizontal.add(id(splitter))

    def setVerticalSplitterVisible(self, col, visible):
        """Устанавливает видимость вертикального разделителя"""
        if col in self.vertical_splitters:
            splitter = self.vertical_splitters[col]
            if visible:
                splitter.show()
                splitter.setHandleWidth(8)
                self.locked_vertical.discard(id(splitter))
            else:
                splitter.hide()
                splitter.setHandleWidth(0)
                self.locked_vertical.add(id(splitter))


class ControlPanel(QWidget):
    def __init__(self, grid):
        super().__init__()
        self.grid = grid
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Горизонтальные разделители
        h_label = QLabel("Горизонтальные разделители:")
        layout.addWidget(h_label)

        for i in range(self.grid.rows - 1):
            row_layout = QHBoxLayout()
            row_layout.addWidget(QLabel(f"Строка {i + 1}-{i + 2}:"))

            for j in range(self.grid.cols):
                cb = QCheckBox(f"Col {j + 1}")
                cb.setChecked(True)
                cb.stateChanged.connect(lambda state, i2=i, j2=j:
                                        self.grid.setHorizontalSplitterVisible(i2, j2, state))
                row_layout.addWidget(cb)

            layout.addLayout(row_layout)

        # Вертикальные разделители
        layout.addSpacing(20)
        v_label = QLabel("Вертикальные разделители:")
        layout.addWidget(v_label)

        for j in range(self.grid.cols - 1):
            cb = QCheckBox(f"Col {j + 1}-{j + 2}")
            cb.setChecked(True)
            cb.stateChanged.connect(lambda state, j2=j:
                                    self.grid.setVerticalSplitterVisible(j2, state))
            layout.addWidget(cb)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel Grid - Complete Splitter Control")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Создаем сетку 4x4
        self.grid = ExcelGrid(4, 4)

        # Создаем панель управления
        control_panel = ControlPanel(self.grid)

        main_layout.addWidget(control_panel)
        main_layout.addWidget(self.grid, 6)

        self.setCentralWidget(central_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())