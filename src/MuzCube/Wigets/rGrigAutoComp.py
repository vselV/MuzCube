import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QLineEdit, QListWidget, QListWidgetItem, QTextEdit)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QTextCursor


class AutoCompleteWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setMaximumHeight(150)
        self.hide()

    def show_at_cursor(self, text_widget):
        if isinstance(text_widget, QTextEdit):
            cursor = text_widget.textCursor()
            rect = text_widget.cursorRect(cursor)
            pos = text_widget.mapToGlobal(QPoint(rect.x(), rect.y() + rect.height()))
            self.move(pos)
        self.show()
        self.setFocus()

    def select_best_match(self):
        if self.count() > 0:
            self.setCurrentRow(0)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            # Навигация вверх
            current_row = self.currentRow()
            if current_row > 0:
                self.setCurrentRow(current_row - 1)
            elif self.count() > 0:
                self.setCurrentRow(self.count() - 1)  # Переход к последнему элементу
            event.accept()

        elif event.key() == Qt.Key.Key_Down:
            # Навигация вниз
            current_row = self.currentRow()
            if current_row < self.count() - 1:
                self.setCurrentRow(current_row + 1)
            elif self.count() > 0:
                self.setCurrentRow(0)  # Переход к первому элементу
            event.accept()

        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Tab):
            # Выбор текущего элемента
            if self.parent() and hasattr(self.parent(), 'insert_current_completion'):
                self.parent().insert_current_completion()
            event.accept()

        elif event.key() == Qt.Key.Key_Escape:
            # Закрытие автодополнения
            self.hide()
            if self.parent():
                self.parent().setFocus()
            event.accept()

        else:
            # Передача остальных клавиш родительскому виджету
            self.hide()
            if self.parent():
                self.parent().setFocus()
                # Создаем новое событие для родителя
                new_event = type(event)(event.type(), event.key(), event.modifiers(), event.text())
                QApplication.sendEvent(self.parent(), new_event)


class AutoCompleteTextEdit(QTextEdit):
    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self.items = items or []
        self.completer = AutoCompleteWidget(self)
        self.completer.itemClicked.connect(self.insert_completion)
        self.completer.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.completer and event.type() == event.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down,
                               Qt.Key.Key_Return, Qt.Key.Key_Enter,
                               Qt.Key.Key_Tab, Qt.Key.Key_Escape):
                # Эти клавиши уже обрабатываются в AutoCompleteWidget
                return False
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        # Если автодополнение видимо, передаем ему управление стрелками
        if self.completer.isVisible():
            if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down,
                               Qt.Key.Key_Return, Qt.Key.Key_Enter,
                               Qt.Key.Key_Tab, Qt.Key.Key_Escape):
                # Передаем событие автодополнению
                self.completer.keyPressEvent(event)
                return

        # Обычная обработка для остальных клавиш
        super().keyPressEvent(event)

        # Показываем автодополнение после ввода текста
        if (event.text() and not event.text().isspace() and
                not event.modifiers() in (Qt.KeyboardModifier.ControlModifier, Qt.KeyboardModifier.AltModifier)):
            QApplication.processEvents()
            self.update_completions()
        else:
            self.completer.hide()

    def focusInEvent(self, event):
        self.completer.hide()
        super().focusInEvent(event)

    def insert_current_completion(self):
        current_item = self.completer.currentItem()
        if current_item:
            self.insert_completion(current_item)

    def get_current_word(self):
        cursor = self.textCursor()
        original_pos = cursor.position()

        # Находим начало слова
        cursor.movePosition(QTextCursor.MoveOperation.StartOfWord)
        word_start = cursor.position()

        # Восстанавливаем позицию и находим конец слова
        cursor.setPosition(original_pos)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfWord)
        word_end = cursor.position()

        # Восстанавливаем оригинальный курсор
        cursor.setPosition(original_pos)
        self.setTextCursor(cursor)

        if word_start < word_end:
            return self.toPlainText()[word_start:word_end], word_start, word_end
        return "", word_start, word_end

    def insert_completion(self, item):
        completion = item.text()
        current_word, word_start, word_end = self.get_current_word()

        cursor = self.textCursor()
        cursor.setPosition(word_start)
        cursor.setPosition(word_end, QTextCursor.MoveMode.KeepAnchor)
        cursor.insertText(completion)

        self.completer.hide()
        self.setFocus()

    def update_completions(self):
        try:
            current_word, _, _ = self.get_current_word()

            if current_word and len(current_word) > 0:
                matches = [item for item in self.items
                           if item.lower().startswith(current_word.lower())]

                if matches:
                    self.completer.clear()
                    for match in matches:
                        self.completer.addItem(QListWidgetItem(match))

                    self.completer.select_best_match()
                    self.completer.show_at_cursor(self)
                    return

            self.completer.hide()

        except Exception as e:
            print(f"Error in update_completions: {e}")
            self.completer.hide()

    def set_items(self, items):
        self.items = items


# Демонстрационное окно с инструкциями
class DemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Автодополнение с навигацией стрелками")
        self.setGeometry(100, 100, 800, 500)

        programming_keywords = [
            "def", "class", "import", "from", "as", "return",
            "if", "else", "elif", "for", "while", "break",
            "continue", "try", "except", "finally", "with",
            "lambda", "global", "nonlocal", "pass", "yield",
            "True", "False", "None", "and", "or", "not", "in", "is",
            "assert", "async", "await", "del", "raise", "super"
        ]

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.text_edit = AutoCompleteTextEdit(programming_keywords)
        self.text_edit.setPlaceholderText(
            "Инструкция:\n"
            "1. Введите 'd' - появится автодополнение\n"
            "2. Используйте ↑ и ↓ для навигации\n"
            "3. Enter/Tab - выбрать текущий вариант\n"
            "4. Esc - закрыть автодополнение\n\n"
            "Попробуйте: 'd' → стрелки → Enter"
        )

        example_code = """def example():
    # Введите 'if' и используйте стрелки
    if True:
        return "test"

# Попробуйте навигацию с несколькими вариантами"""

        self.text_edit.setPlainText(example_code)
        layout.addWidget(self.text_edit)
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())