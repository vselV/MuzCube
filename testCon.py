from PyQt6.QtWidgets import QPushButton, QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt
import sys


class MultiHandlerDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Multiple Handlers Demo")
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Создаем кнопку
        self.button = QPushButton("Нажми меня!")
        layout.addWidget(self.button)

        # Создаем метку для вывода
        self.output_label = QLabel("Ожидание нажатия...")
        self.output_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.output_label)

        # Подключаем несколько обработчиков к одному сигналу
        self.button.clicked.connect(self.handler1)
        self.button.clicked.connect(self.handler2)
        self.button.clicked.connect(self.handler3)

        central_widget.setLayout(layout)

    def handler1(self):
        """Первый обработчик"""
        print("Handler 1: Кнопка нажата!")

    def handler2(self):
        """Второй обработчик"""
        current_text = self.output_label.text()
        self.output_label.setText(f"{current_text}\nHandler 2 сработал")

    def handler3(self):
        """Третий обработчик"""
        self.output_label.setText("Все обработчики выполнены!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MultiHandlerDemo()
    window.show()
    sys.exit(app.exec())