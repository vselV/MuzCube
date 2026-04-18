import sys
from PyQt6.QtWidgets import QApplication, QPlainTextEdit, QWidget, QVBoxLayout
from PyQt6.QtGui import QTextCharFormat, QColor, QSyntaxHighlighter, QFont, QTextDocument
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread, pyqtSlot
from pygments.token import Token
from pygments.lexer import LexerContext
#import MuzCubeLexer
from src.MuzCube.Lex import MuzCubeLexer

class StateManager:
    def __init__(self):
        self.block_states = {}  # key: block_number, value: stack
        self.block_positions = {}  # key: block.position(), value: block_number

    def update_block_numbers(self, document):
        """Обновляет нумерацию блоков с использованием позиций"""
        block = document.firstBlock()
        block_number = 0
        new_positions = {}
        states_to_keep = {}

        while block.isValid():
            pos = block.position()
            new_positions[pos] = block_number

            # Переносим существующие состояния
            if pos in self.block_positions:
                old_num = self.block_positions[pos]
                if old_num in self.block_states:
                    states_to_keep[block_number] = self.block_states[old_num]

            block = block.next()
            block_number += 1

        self.block_positions = new_positions
        self.block_states = states_to_keep

    def get_stack(self, block):
        """Возвращает стек для указанного блока"""
        pos = block.position()
        block_number = self.block_positions.get(pos, -1)
        if block_number > 0:
            prev_pos = block.previous().position()
            prev_num = self.block_positions.get(prev_pos, -1)
            return self.block_states.get(prev_num, ["root"]).copy()
        return ["root"]

    def set_stack(self, block, stack):
        """Сохраняет стек для блока"""
        pos = block.position()
        block_number = self.block_positions.get(pos, -1)
        if block_number >= 0:
            self.block_states[block_number] = stack


class AsyncLexer(QObject):
    tokens_ready = pyqtSignal(list, object, object)  # tokens, start_pos, end_pos

    def __init__(self):
        super().__init__()
        self.lexer = MuzCubeLexer.MuzCubeLexer()
        self.moveToThread(QThread.currentThread())

    @pyqtSlot(str, object)
    def process_text(self, text, context=None):
        try:
            tokens = list(self.lexer.get_tokens_unprocessed(context=context))
            self.tokens_ready.emit(tokens, 0, len(text))
        except Exception as e:
            print(f"Lexer error: {e}")


class ContextAwareHighlighter(QSyntaxHighlighter):
    def __init__(self, document: QTextDocument,**kwargs):
        super().__init__(document)
        self.state_manager = StateManager()
        self.async_lexer = AsyncLexer()
        self.async_lexer.tokens_ready.connect(self.apply_highlighting)
        self.styles = kwargs.get("style")
        self.setup_styles()

        self.lexer_thread = QThread()
        self.async_lexer.moveToThread(self.lexer_thread)
        self.lexer_thread.start()

    def setup_styles(self):
        if self.styles is None:
            print(self.styles)
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
        block = self.currentBlock()
        self.state_manager.update_block_numbers(self.document())

        # Получаем стек из предыдущего блока
        stack = self.state_manager.get_stack(block)
        context = LexerContext(text=text + '\n', stack=stack, pos=0)

        # Обрабатываем текст асинхронно
        self.async_lexer.process_text(text, context)

        # Сохраняем состояние стека для следующего блока
        if hasattr(context, 'stack'):
            self.state_manager.set_stack(block, context.stack)

    @pyqtSlot(list, object, object)
    def apply_highlighting(self, tokens, start_pos, end_pos):
        for pos, token, value in tokens:
         #   print(self.styles)
            fmt = self.styles.get(token, self.styles[Token.Text])
            self.setFormat(pos, len(value), fmt)


class StableCodeEditor(QPlainTextEdit):
    def __init__(self,**kwargs):
        super().__init__()
        self.setup_editor()
        self.highlighter = ContextAwareHighlighter(self.document(),**kwargs)
        self._navigation_keys = {
            Qt.Key.Key_Left, Qt.Key.Key_Right,
            Qt.Key.Key_Up, Qt.Key.Key_Down,
            Qt.Key.Key_PageUp, Qt.Key.Key_PageDown,
            Qt.Key.Key_Home, Qt.Key.Key_End
        }
        self.style = kwargs.get("style")
        self.pt = kwargs.get("font_size",14)

    def setup_editor(self):
        bg = '#1e1e1e'
        sel = '#264F78'
        if self.style is not None:
            bg = self.style.get('background_st')
            sel = self.style.get('selected_st')
        self.setStyleSheet("""
            QPlainTextEdit {"""
                           +
        f"""
                background-color: {bg};
                color: #d4d4d4;
                font-family: Consolas;
                font-size: {self.pt}pt;
                selection-background-color: {sel};
        """
                           +
        """
            }
        """)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

    def keyPressEvent(self, event):
        cursor = self.textCursor()
        scroll_pos = self.verticalScrollBar().value()

        # Проверяем, является ли клавиша навигационной
        is_navigation = event.key() in self._navigation_keys
        is_modified = event.modifiers() in (Qt.KeyboardModifier.NoModifier, Qt.KeyboardModifier.ShiftModifier)

        if is_navigation and is_modified:
            # Для навигационных клавиш - стандартная обработка без обновления подсветки
            super().keyPressEvent(event)
            self.verticalScrollBar().setValue(scroll_pos)
        else:
            # Для всех остальных клавиш - обычная обработка с обновлением подсветки
            super().keyPressEvent(event)

            # Обновляем подсветку только если это не навигация
            block = self.document().findBlock(cursor.position())
            self.highlighter.rehighlightBlock(block)

            # Обновляем следующий блок для многострочных конструкций
            next_block = block.next()
            if next_block.isValid():
                self.highlighter.rehighlightBlock(next_block)

            self.verticalScrollBar().setValue(scroll_pos)

    def closeEvent(self, event):
        self.highlighter.lexer_thread.quit()
        self.highlighter.lexer_thread.wait()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = StableCodeEditor()
    editor.setPlainText("")

    window = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(editor)
    window.setLayout(layout)
    window.show()
    sys.exit(app.exec())