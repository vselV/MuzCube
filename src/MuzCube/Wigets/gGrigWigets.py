import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QLineEdit, QListWidget, QListWidgetItem, QLabel)
from PyQt6.QtCore import Qt, QPoint


class SearchDropdownWidget(QWidget):
    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self.items = items or []
        self.filtered_items = self.items.copy()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Текстовое поле для поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск...")
        self.search_input.textChanged.connect(self.filter_items)
        self.search_input.installEventFilter(self)

        # Выпадающий список
        self.dropdown_list = QListWidget()
        self.dropdown_list.setMaximumHeight(150)
        self.dropdown_list.hide()
        self.dropdown_list.itemClicked.connect(self.select_item)
        self.dropdown_list.installEventFilter(self)

        layout.addWidget(self.search_input)
        layout.addWidget(self.dropdown_list)

        self.populate_list()

    def eventFilter(self, obj, event):
        # Обработка событий для search_input
        if obj == self.search_input and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Down:
                self.show_dropdown_and_focus()
                return True
            elif event.key() == Qt.Key.Key_Tab and self.dropdown_list.isVisible():
                self.select_current_item()
                return True
            elif event.key() == Qt.Key.Key_Escape and self.dropdown_list.isVisible():
                self.dropdown_list.hide()
                return True

        # Обработка событий для dropdown_list
        elif obj == self.dropdown_list and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Up:
                self.navigate_dropdown(-1)
                return True
            elif event.key() == Qt.Key.Key_Down:
                self.navigate_dropdown(1)
                return True
            elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Tab):
                self.select_current_item()
                return True
            elif event.key() == Qt.Key.Key_Escape:
                self.dropdown_list.hide()
                self.search_input.setFocus()
                return True

        return super().eventFilter(obj, event)

    def show_dropdown_and_focus(self):
        """Показывает выпадающий список и устанавливает фокус на него"""
        if self.filtered_items and not self.dropdown_list.isVisible():
            self.dropdown_list.show()
        if self.dropdown_list.isVisible():
            self.dropdown_list.setFocus()
            if self.dropdown_list.currentItem() is None and self.dropdown_list.count() > 0:
                self.dropdown_list.setCurrentRow(0)

    def navigate_dropdown(self, direction):
        """Навигация по выпадающему списку"""
        if not self.dropdown_list.isVisible():
            return

        current_row = self.dropdown_list.currentRow()
        new_row = current_row + direction

        # Циклическая навигация
        if new_row < 0:
            new_row = self.dropdown_list.count() - 1
        elif new_row >= self.dropdown_list.count():
            new_row = 0

        self.dropdown_list.setCurrentRow(new_row)

    def select_current_item(self):
        """Выбирает текущий элемент из выпадающего списка"""
        if self.dropdown_list.isVisible():
            current_item = self.dropdown_list.currentItem()
            if current_item:
                self.select_item(current_item)
            elif self.dropdown_list.count() > 0:
                # Если нет выбранного элемента, выбираем первый
                self.dropdown_list.setCurrentRow(0)
                self.select_item(self.dropdown_list.currentItem())

    def populate_list(self):
        self.dropdown_list.clear()
        for item in self.filtered_items:
            list_item = QListWidgetItem(str(item))
            self.dropdown_list.addItem(list_item)

    def filter_items(self, text):
        text = text.lower()
        if not text:
            self.filtered_items = self.items.copy()
            self.dropdown_list.hide()
        else:
            self.filtered_items = [item for item in self.items
                                   if text in str(item).lower()]
            self.populate_list()
            if self.filtered_items:
                self.dropdown_list.show()
                # Автоматически выбираем первый элемент
                if self.dropdown_list.count() > 0:
                    self.dropdown_list.setCurrentRow(0)
            else:
                self.dropdown_list.hide()

    def select_item(self, item):
        self.search_input.setText(item.text())
        self.dropdown_list.hide()
        self.search_input.setFocus()

    def set_items(self, items):
        self.items = items
        self.filtered_items = items.copy()
        self.populate_list()

    def get_selected_item(self):
        """Возвращает выбранный элемент"""
        return self.search_input.text()


class EnhancedSearchDropdownWidget(SearchDropdownWidget):
    """Расширенная версия с дополнительными возможностями"""

    def __init__(self, items=None, parent=None):
        super().__init__(items, parent)
        self.setup_advanced_features()

    def setup_advanced_features(self):
        """Дополнительные настройки для улучшенного виджета"""
        # Стилизация для лучшего UX
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #007acc;
            }
        """)

        self.dropdown_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #007acc;
                border-top: none;
                background-color: white;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #007acc;
                color: white;
            }
            QListWidget::item:hover:!selected {
                background-color: #f0f0f0;
            }
        """)

    def keyPressEvent(self, event):
        """Дополнительная обработка клавиш"""
        if event.key() == Qt.Key.Key_Up and self.dropdown_list.isVisible():
            self.navigate_dropdown(-1)
            return
        elif event.key() == Qt.Key.Key_Down and self.dropdown_list.isVisible():
            self.navigate_dropdown(1)
            return
        super().keyPressEvent(event)

#class SearchWin(QWidget):


# Демонстрационное окно
class DemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Улучшенный поиск с автодополнением")
        self.setGeometry(100, 100, 500, 300)

        # Пример данных
        sample_data = [
            "Яблоко", "Банан", "Апельсин", "Груша", "Виноград",
            "Лимон", "Лайм", "Манго", "Киви", "Ананас",
            "Персик", "Нектарин", "Слива", "Вишня", "Черешня",
            "Клубника", "Малина", "Черника", "Ежевика", "Арбуз",
            "Дыня", "Гранат", "Инжир", "Хурма", "Фейхоа"
        ]

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Простая версия
        simple_label = QLabel("Простая версия:")
        simple_search = SearchDropdownWidget(sample_data)

        # Улучшенная версия
        enhanced_label = QLabel("Улучшенная версия со стилями:")
        enhanced_search = EnhancedSearchDropdownWidget(sample_data)

        # Инструкция
        instruction = QLabel(
            "Инструкция:\n"
            "• Введите текст для поиска\n"
            "• ↓ - открыть список и перейти к нему\n"
            "• ↑/↓ - навигация по списку\n"
            "• Tab/Enter - выбрать текущий вариант\n"
            "• Esc - закрыть список\n"
            "• Клик - выбрать элемент"
        )
        instruction.setStyleSheet("color: #666; font-size: 12px;")

        layout.addWidget(simple_label)
        layout.addWidget(simple_search)
        layout.addWidget(enhanced_label)
        layout.addWidget(enhanced_search)
        layout.addWidget(instruction)

        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = DemoWindow()
    window.show()

    sys.exit(app.exec())