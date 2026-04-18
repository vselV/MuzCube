import sys
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QListWidget,
                             QListWidgetItem, QLineEdit, QLabel, QPushButton)
from PyQt6.QtCore import Qt


class SearchDialog(QDialog):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.items = items
        self.filtered_items = items.copy()
        self.selected_text = ""
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Поиск")
        self.setGeometry(300, 300, 400, 300)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Поле поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите текст для поиска...")
        self.search_input.textChanged.connect(self.filter_items)
        self.search_input.installEventFilter(self)

        # Список результатов
        self.result_list = QListWidget()
        self.result_list.itemDoubleClicked.connect(self.accept_selection)
        self.result_list.installEventFilter(self)

        layout.addWidget(QLabel("Поиск:"))
        layout.addWidget(self.search_input)
        layout.addWidget(QLabel("Результаты:"))
        layout.addWidget(self.result_list)

        # Заполняем初始列表
        self.populate_list()
        self.search_input.setFocus()

    def eventFilter(self, obj, event):
        # Обработка событий для поля ввода
        if obj == self.search_input and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Tab:
                # Tab - подставить самый подходящий вариант
                self.auto_complete()
                return True
            elif event.key() == Qt.Key.Key_Down:
                # Стрелка вниз - перейти к списку
                self.result_list.setFocus()
                if self.result_list.count() > 0:
                    self.result_list.setCurrentRow(0)
                return True
            elif event.key() == Qt.Key.Key_Return:
                # Enter - принять диалог с текущим текстом
                self.selected_text = self.search_input.text()
                self.accept()
                return True

        # Обработка событий для списка
        elif obj == self.result_list and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Up:
                # Стрелка вверх
                current_row = self.result_list.currentRow()
                if current_row > 0:
                    self.result_list.setCurrentRow(current_row - 1)
                return True
            elif event.key() == Qt.Key.Key_Down:
                # Стрелка вниз
                current_row = self.result_list.currentRow()
                if current_row < self.result_list.count() - 1:
                    self.result_list.setCurrentRow(current_row + 1)
                return True
            elif event.key() == Qt.Key.Key_Return:
                # Enter - выбрать текущий элемент
                current_item = self.result_list.currentItem()
                if current_item:
                    self.selected_text = current_item.text()
                    self.accept()
                return True
            elif event.key() == Qt.Key.Key_Tab:
                # Tab - выбрать текущий элемент
                current_item = self.result_list.currentItem()
                if current_item:
                    self.selected_text = current_item.text()
                    self.accept()
                return True
            elif event.key() == Qt.Key.Key_Escape:
                # Esc - вернуться к полю ввода
                self.search_input.setFocus()
                return True

        return super().eventFilter(obj, event)

    def auto_complete(self):
        """Автодополнение - подставляет самый подходящий вариант"""
        if self.filtered_items:
            best_match = str(self.filtered_items[0])
            self.search_input.setText(best_match)
            self.search_input.setCursorPosition(len(best_match))

    def filter_items(self, text):
        text = text.lower()
        if not text:
            self.filtered_items = self.items.copy()
        else:
            self.filtered_items = [item for item in self.items
                                   if text in str(item).lower()]
        self.populate_list()

    def populate_list(self):
        self.result_list.clear()
        for item in self.filtered_items:
            list_item = QListWidgetItem(str(item))
            self.result_list.addItem(list_item)

    def accept_selection(self, item):
        """Обработка двойного клика по элементу"""
        self.selected_text = item.text()
        self.accept()

    def get_selected_text(self):
        """Возвращает выбранный текст"""
        return self.selected_text


# Простая функция для использования
def show_search_dialog(items, parent=None, title="Поиск"):
    """Показывает диалог поиска и возвращает выбранный текст"""
    dialog = SearchDialog(items, parent)
    dialog.setWindowTitle(title)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_selected_text()
    return None


# Пример использования
if __name__ == "__main__":
    app = QApplication(sys.argv)

    sample_data = [
        "Яблоко", "Банан", "Апельсин", "Груша", "Виноград",
        "Лимон", "Лайм", "Манго", "Киви", "Ананас",
        "Персик", "Нектарин", "Слива", "Вишня", "Черешня"
    ]

    # Использование диалога
    result = show_search_dialog(sample_data, None, "Выберите фрукт")

    if result:
        print(f"Выбран: {result}")
    else:
        print("Диалог отменен")

    # Завершаем приложение
    sys.exit()