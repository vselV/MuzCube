import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                             QTextEdit, QLineEdit, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal


class ConsoleWidget(QWidget):
    command_executed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Область вывода консоли
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: black;
                color: #00ff00;
                font-family: Consolas, Monospace;
                font-size: 12px;
            }
        """)
        #layout.addWidget(self.output)

        # Поле ввода команд
        self.input = QLineEdit()
        self.input.setStyleSheet("""
            QLineEdit {
                background-color: black;
                color: white;
                font-family: Consolas, Monospace;
                font-size: 12px;
                border: 1px solid #00ff00;
            }
        """)
        self.input.returnPressed.connect(self.execute_command)
        layout.addWidget(self.input)

    def execute_command(self):
        command = self.input.text()
        self.append_output(f"> {command}")
        self.command_executed.emit(command)
        self.input.clear()

    def append_output(self, text):
        self.output.append(text)
        # Автопрокрутка вниз
        scrollbar = self.output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear(self):
        self.output.clear()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Консольный виджет")
        self.setGeometry(100, 100, 600, 400)

        self.console = ConsoleWidget()
        self.console.command_executed.connect(self.handle_command)

        self.setCentralWidget(self.console)

        # Тестовый вывод
        self.console.append_output("Добро пожаловать в консольный виджет!")
        self.console.append_output("Введите команду и нажмите Enter...")

    def handle_command(self, command):
        # Здесь можно обрабатывать команды
        if command.lower() == "clear":
            self.console.clear()
        elif command.lower() == "exit":
            self.close()
        else:
            self.console.append_output(f"Выполнено: {command}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())