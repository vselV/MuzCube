import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout,
                             QGraphicsView, QGraphicsScene, QLabel, QPushButton,
                             QTextEdit, QFrame, QSpinBox, QComboBox)
from PyQt6.QtCore import Qt


class AdvancedSeamlessContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_layout = QGridLayout(self)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(0)
        self.widgets = {}

    def add_to_grid(self, widget, row, column, row_span=1, column_span=1):
        """Базовый метод добавления виджета в сетку"""
        self.grid_layout.addWidget(widget, row, column, row_span, column_span)

        # Убираем рамки для поддерживаемых виджетов
        if isinstance(widget, (QGraphicsView, QFrame)):
            widget.setFrameShape(QFrame.Shape.NoFrame)

        if isinstance(widget, QGraphicsView):
            widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Сохраняем ссылку
        key = f"{row}_{column}"
        self.widgets[key] = widget
        return widget

    # Фабричные методы для разных типов виджетов
    def add_graphics_scene(self, row, column, row_span=1, column_span=1, bg_color=Qt.GlobalColor.white):
        scene = QGraphicsScene()
        scene.setBackgroundBrush(bg_color)
        view = QGraphicsView(scene)
        return self.add_to_grid(view, row, column, row_span, column_span), scene

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

    def add_text_edit(self, row, column, row_span=1, column_span=1, text=""):
        text_edit = QTextEdit(text)
        text_edit.setFrameShape(QFrame.Shape.NoFrame)
        return self.add_to_grid(text_edit, row, column, row_span, column_span)

    def add_spinbox(self, row, column, row_span=1, column_span=1, min_val=0, max_val=100):
        spinbox = QSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setFrame(False)
        return self.add_to_grid(spinbox, row, column, row_span, column_span)

    def add_combobox(self, row, column, row_span=1, column_span=1, items=None):
        combobox = QComboBox()
        combobox.setFrame(False)
        if items:
            combobox.addItems(items)
        return self.add_to_grid(combobox, row, column, row_span, column_span)

    # Управление сеткой
    def set_stretch(self, rows=None, columns=None):
        if rows:
            for row, stretch in rows.items():
                self.grid_layout.setRowStretch(row, stretch)
        if columns:
            for col, stretch in columns.items():
                self.grid_layout.setColumnStretch(col, stretch)

    def set_minimum_sizes(self, rows=None, columns=None):
        if rows:
            for row, size in rows.items():
                self.grid_layout.setRowMinimumHeight(row, size)
        if columns:
            for col, size in columns.items():
                self.grid_layout.setColumnMinimumWidth(col, size)


# Пример использования расширенного класса
class AdvancedExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Расширенная бесшовная сетка")
        self.setGeometry(100, 100, 1200, 700)

        container = AdvancedSeamlessContainer()
        self.setCentralWidget(container)

        # Создаем сложную сетку
        container.add_graphics_scene(0, 0, 2, 1, Qt.GlobalColor.blue)
        container.add_graphics_scene(0, 1, 2, 1, Qt.GlobalColor.red)

        container.add_label("Панель управления", 0, 2, 1, 2,
                            style="background: #333; color: white; font-size: 14px;")

        container.add_button("Старт", 1, 2)
        container.add_button("Стоп", 1, 3)

        container.add_text_edit(2, 0, 1, 2, "Текстовое поле\nМногострочный текст")

        container.add_spinbox(2, 2, 1, 1, 0, 100)
        container.add_combobox(2, 3, 1, 1, ["Опция 1", "Опция 2", "Опция 3"])

        # Настраиваем растяжение
        container.set_stretch(
            rows={0: 2, 1: 1, 2: 1},
            columns={0: 1, 1: 1, 2: 1, 3: 1}
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdvancedExample()
    window.show()
    sys.exit(app.exec())