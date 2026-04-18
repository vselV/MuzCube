import sys
from lib2to3.fixes.fix_input import context

from PyQt6.QtWidgets import QApplication, QPlainTextEdit, QWidget, QVBoxLayout
from PyQt6.QtGui import QTextCharFormat, QColor, QSyntaxHighlighter, QFont
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread, pyqtSlot
from pygments.lexers import PythonLexer
from pygments.token import Token
from pygments.lexer import LexerContext
import MuzCubeLexer

def soborContext(text,stack):
    return LexerContext(text=text,stack=stack,pos=0)

class AsyncLexer(QObject):
    tokens_ready = pyqtSignal(list, object, object)  # tokens, start_pos, end_pos

    def __init__(self):
        super().__init__()
        self.lexer = MuzCubeLexer.MuzCubeLexer()
        self.moveToThread(QThread.currentThread())

    @pyqtSlot(str, object)
    def process_text(self, text, context = None):
        try:
            tokens = list(self.lexer.get_tokens_unprocessed(context=context))
            self.tokens_ready.emit(tokens, 0, len(text))

        except Exception as e:
            print(f"Lexer error: {e}")


class ResponsiveHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.setup_styles()
        self.async_lexer = AsyncLexer()
        self.async_lexer.tokens_ready.connect(self.apply_highlighting)
        self.lexer_thread = QThread()
        self.async_lexer.moveToThread(self.lexer_thread)
        self.lexer_thread.start()

        self.string_pose = 0
        self.stack_list = []

    def setup_styles(self):
        self.styles = {
            Token.Keyword: self.create_style(QColor(255, 100, 100)),
            Token.Name.Function: self.create_style(QColor(100, 200, 255)),
            Token.String: self.create_style(QColor(100, 255, 100)),
            Token.Comment: self.create_style(QColor(150, 150, 150)),
            Token.Number: self.create_style(QColor(255, 200, 100)),
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
        # Отправляем текст на обработку в отдельном потоке
        context = soborContext(text,["root",])
        self.async_lexer.process_text(text,context)
        print(context)

    @pyqtSlot(list, object, object)
    def apply_highlighting(self, tokens, start_pos, end_pos):
        for pos, token, value in tokens:
            fmt = self.styles.get(token, self.styles[Token.Text])
            self.setFormat(pos, len(value), fmt)


class InstantCodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setup_editor()
        self.highlighter = ResponsiveHighlighter(self.document())

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

        # Обновляем только видимую область
        self.highlighter.rehighlightBlock(self.document().findBlock(cursor.position()))

        self.verticalScrollBar().setValue(scroll_pos)
        self.setTextCursor(cursor)

    def closeEvent(self, event):
        self.highlighter.lexer_thread.quit()
        self.highlighter.lexer_thread.wait()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Сначала показываем окно
    window = QWidget()
    layout = QVBoxLayout()
    editor = InstantCodeEditor()
    editor.setPlainText("""# Редактор загружается мгновенно
def hello():
    print("Hello World!")

class Example:
    def __init__(self):
        self.value = 42""")

    layout.addWidget(editor)
    window.setLayout(layout)
    window.show()

    sys.exit(app.exec())