import sys

from PyQt6.QtNetwork.QUdpSocket import kwargs
from PyQt6.QtWidgets import QApplication, QPlainTextEdit, QWidget, QVBoxLayout
from PyQt6.QtGui import QTextCharFormat, QColor, QSyntaxHighlighter, QFont
from PyQt6.QtCore import Qt
from pygments.lexers import PythonLexer
import MuzCubeLexer
from pygments.token import Token


class CorrectHighlighter(QSyntaxHighlighter):
    def __init__(self, document,**kwargs):
        super().__init__(document)
        self.lexer = kwargs.get("lexer", PythonLexer())
        self.setup_styles()

    def setup_styles(self):
        self.styles = {
            Token.Keyword: self.create_style(QColor(255, 100, 100)),
            Token.Name.Function: self.create_style(QColor(100, 200, 255)),
            Token.String: self.create_style(QColor(100, 255, 100)),
            Token.Comment: self.create_style(QColor(150, 150, 150)),
            Token.Number: self.create_style(QColor(255, 0, 100)),
            Token.Operator: self.create_style(QColor(255, 255, 255)),
            Token.Name: self.create_style(QColor(220, 220, 220)),
            Token.Text: self.create_style(QColor(220, 220, 220))
        }

    def create_style(self, color):
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        fmt.setFont(QFont("Consolas", 12))
        return fmt

    def highlightBlock(self, text):
        if not text.strip():
            return

        block = self.currentBlock()
        block_pos = block.position()
        block_length = len(text)

        # Получаем токены с их абсолютными позициями
        tokens = list(self.lexer.get_tokens_unprocessed(text))

        for pos, token, value in tokens:
            # Проверяем, попадает ли токен в текущий блок
            if pos >= block_length:
                continue

            length = len(value)
            end_pos = pos + length

            # Определяем стиль для токена
            if token in Token.Keyword:
                # Проверяем, является ли значение целым ключевым словом
                if value in {'for', 'in', 'while', 'if', 'else', 'def', 'return'}:
                    fmt = self.styles[Token.Keyword]
                else:
                    fmt = self.styles[Token.Name]
            else:
                print(token)
                fmt = self.styles.get(token, self.styles[Token.Text])

            self.setFormat(pos, length, fmt)


class FinalEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setup_editor()
        self.highlighter = CorrectHighlighter(self.document())

    def setup_editor(self):
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: Consolas;
                font-size: 12pt;
                selection-background-color: #264F78;
            }
        """)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

    def keyPressEvent(self, event):
        cursor = self.textCursor()
        scroll_pos = self.verticalScrollBar().value()

        super().keyPressEvent(event)
        self.highlighter.rehighlight()

        self.verticalScrollBar().setValue(scroll_pos)
        self.setTextCursor(cursor)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = FinalEditor()
    editor.setPlainText("""# Теперь работает идеально!
for i in range(10):  # Все символы подсвечиваются правильно
for f in range(5):   # Буква 'f' не ломает подсветку
for item in items:   # Полные слова работают корректно
    print(f"Item: {item}")""")

    window = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(editor)
    window.setLayout(layout)
    window.show()
    sys.exit(app.exec())