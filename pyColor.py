import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QColorDialog, QLineEdit, QLabel, QPushButton)
from PyQt6.QtGui import QColor, QClipboard
from PyQt6.QtCore import Qt


class ColorPickerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Настройка главного окна
        self.setWindowTitle('Color Picker')
        self.setFixedSize(300, 150)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        layout = QVBoxLayout(central_widget)

        # Кнопка для выбора цвета
        self.color_button = QPushButton('Выбрать цвет')
        self.color_button.clicked.connect(self.open_color_dialog)
        layout.addWidget(self.color_button)

        # Метка для отображения текущего цвета
        self.color_label = QLabel('Текущий цвет:')
        layout.addWidget(self.color_label)

        # Поле для отображения RGB значений
        self.rgb_text = QLineEdit()
        self.rgb_text.setReadOnly(True)
        self.rgb_text.setPlaceholderText('RGB значения появятся здесь')
        self.rgb_text.mousePressEvent = self.copy_to_clipboard
        layout.addWidget(self.rgb_text)

        # Инициализация начального цвета
        self.current_color = QColor(255, 255, 255)
        self.update_color_display()

    def open_color_dialog(self):
        # Открытие диалога выбора цвета
        color = QColorDialog.getColor(self.current_color, self, 'Выберите цвет')
        if color.isValid():
            self.current_color = color
            self.update_color_display()

    def update_color_display(self):
        # Обновление отображения цвета и RGB значений
        # Установка цвета фона для кнопки
        self.color_button.setStyleSheet(f"background-color: {self.current_color.name()};")

        # Отображение RGB значений
        rgb_values = f"{self.current_color.red()}, {self.current_color.green()}, {self.current_color.blue()}"
        self.rgb_text.setText(rgb_values)

        # Обновление метки
        self.color_label.setText(f'Текущий цвет: {rgb_values}')

    def copy_to_clipboard(self, event):
        # Копирование RGB значений в буфер обмена при клике на текстовое поле
        clipboard = QApplication.clipboard()
        clipboard.setText(self.rgb_text.text())

        # Временное изменение текста для подтверждения копирования
        original_text = self.rgb_text.text()
        self.rgb_text.setText('Скопировано в буфер!')

        # Восстановление оригинального текста через 1 секунду
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1000, lambda: self.rgb_text.setText(original_text))

        # Вызов оригинального обработчика события
        QLineEdit.mousePressEvent(self.rgb_text, event)


def main():
    app = QApplication(sys.argv)
    window = ColorPickerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()