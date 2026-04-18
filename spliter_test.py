import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QSplitter, QTextEdit, QCheckBox, QVBoxLayout, QHBoxLayout, QSplitterHandle)
from PyQt6.QtCore import Qt


class LockableSplitterHandle(QSplitterHandle):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.locked = False

    def mousePressEvent(self, event):
        if not self.locked and event.button() == Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if not self.locked:
            super().mouseMoveEvent(event)
        else:
            event.ignore()

    def setLocked(self, locked):
        self.locked = locked
        self.setVisible(False)
        self.setFixedSize(0, 0)
        if locked:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self.setCursor(Qt.CursorShape.SplitHCursor if self.orientation() == Qt.Orientation.Horizontal
                           else Qt.CursorShape.SplitVCursor)


class LockableSplitter(QSplitter):
    def __init__(self, orientation):
        super().__init__(orientation)
        self.locked_handles = set()

    def createHandle(self):
        handle = LockableSplitterHandle(self.orientation(), self)
        return handle

    def lockHandle(self, index, locked=True):
        """Блокирует или разблокирует handle по индексу"""
        if 0 <= index < self.count() - 1:
            handle = self.handle(index)
            if isinstance(handle, LockableSplitterHandle):
                handle.setLocked(locked)
                if locked:
                    self.locked_handles.add(index)
                else:
                    self.locked_handles.discard(index)

    def isHandleLocked(self, index):
        """Проверяет, заблокирован ли handle"""
        return index in self.locked_handles

class SimpleExcelGrid(LockableSplitter):
    def __init__(self, rows=3, cols=3):
        super().__init__(Qt.Orientation.Horizontal)  # Меняем на горизонтальную ориентацию
        self.rows = rows
        self.cols = cols
        self.vertical_splitters = []  # Храним вертикальные сплиттеры для управления
        self.horizontal_splitters = []  # Храним горизонтальные сплиттеры
        self.initUI()

    def initUI(self):
        self.setHandleWidth(5)
        self.setStyleSheet("QSplitter::handle { background-color: #cccccc; }")

        # Создаем колонки (теперь это основные контейнеры)
        for j in range(self.cols):
            col_splitter = LockableSplitter(Qt.Orientation.Vertical)  # Меняем на вертикальную ориентацию
            col_splitter.setHandleWidth(5)
            col_splitter.setStyleSheet("QSplitter::handle { background-color: #cccccc; }")

            # Создаем ячейки в колонке
            for i in range(self.rows):
                cell = QTextEdit(f"Row {i + 1}, Col {j + 1}")
                cell.setContentsMargins(0,0,0,0)
                cell.setMinimumSize(100, 50)
                col_splitter.addWidget(cell)

            self.addWidget(col_splitter)
            self.vertical_splitters.append(col_splitter)

        # Синхронизируем горизонтальные разделители между колонками
        self.sync_horizontal_splitters()

    def sync_horizontal_splitters(self):
        """Синхронизирует горизонтальные разделители между колонками"""
        if self.count() < 2:
            return

        # Берем первую колонку как мастер
        master_col = self.widget(0)

        def sync_handler(pos, index):
            for j in range(0, self.count()):
                col = self.widget(j)
                col.blockSignals(True)
                col.moveSplitter(pos, index)
                col.blockSignals(False)

        # Подключаем сигналы от мастера ко всем остальным колонкам
        for j in range(self.cols):
            self.widget(j).splitterMoved.connect(sync_handler)

    def set_splitter_visible(self, row_index, col_index, visible):
        """Устанавливает видимость разделителя"""
        if row_index < 0 or row_index >= self.rows - 1 or col_index < 0 or col_index >= self.cols:
            return

        # Для горизонтальных разделителей (между строками)
        handle_index = row_index
        for j in range(self.cols):
            col = self.widget(j)
            handle = col.handle(handle_index)
            if handle:
                handle.setVisible(visible)
                # Также отключаем функциональность, если невидимый
                col.setChildrenCollapsible(visible)

    def set_splitter_enabled(self, row_index, col_index, enabled):
        """Включает/отключает функциональность разделителя"""
        if row_index < 0 or row_index >= self.rows - 1 or col_index < 0 or col_index >= self.cols:
            return

        # Для горизонтальных разделителей (между строками)
        handle_index = row_index
        col = self.widget(col_index)
        if col:
            col.setChildrenCollapsible(enabled)
            # Блокируем сигналы, если отключен
            if not enabled:
                col.blockSignals(not enabled)

    def lockHorizontalSplitter(self, row_index, col_index, locked=True):
        """Блокирует горизонтальный разделитель между строками"""
        if 0 <= col_index < self.cols and 0 <= row_index < self.rows - 1:
            col_splitter = self.vertical_splitters[col_index]
            col_splitter.lockHandle(row_index, locked)

    def lockVerticalSplitter(self, col_index, locked=True):
        """Блокирует вертикальный разделитель между колонками"""
        if 0 <= col_index < self.cols - 1:
            self.lockHandle(col_index, locked)


class ControlPanel(QWidget):
    def __init__(self, grid):
        super().__init__()
        self.grid = grid
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Контролы для горизонтальных разделителей
        h_label = QCheckBox("Горизонтальные разделители (между строками)")
        h_label.setChecked(True)
        h_label.stateChanged.connect(self.toggle_all_horizontal)
        layout.addWidget(h_label)

        # Контролы для вертикальных разделителей
        v_label = QCheckBox("Вертикальные разделители (между колонками)")
        v_label.setChecked(True)
        v_label.stateChanged.connect(self.toggle_all_vertical)
        layout.addWidget(v_label)

        self.setLayout(layout)

    def toggle_all_horizontal(self, state):
        visible = state == Qt.CheckState.Checked.value
        for i in range(self.grid.rows - 1):
            for j in range(self.grid.cols):
                self.grid.set_splitter_visible(i, j, visible)
                self.grid.set_splitter_enabled(i, j, visible)

    def toggle_all_vertical(self, state):
        visible = state == Qt.CheckState.Checked.value
        for j in range(self.grid.cols - 1):
            self.grid.set_vertical_splitter_visible(j, visible)
            self.grid.set_vertical_splitter_enabled(j, visible)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Excel Grid")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Создаем сетку
        self.grid = SimpleExcelGrid(4, 4)
        self.grid.lockVerticalSplitter(1)

        # Создаем панель управления
        control_panel = ControlPanel(self.grid)

        main_layout.addWidget(control_panel)
        main_layout.addWidget(self.grid, 1)

        self.setCentralWidget(central_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())