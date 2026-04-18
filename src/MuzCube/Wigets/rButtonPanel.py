from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal

def setStyleBtns(mass,style):
    for btn in mass:
        btn.setStyleSheet(style)

class ButtonPanel(QWidget):
    """Гибкая панель с кнопками, которую можно добавить в любое место."""
    buttonClicked = pyqtSignal(str)  # Сигнал с текстом кнопки

    def __init__(self, parent=None):
        self.dictBtn = {}
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        self.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                min-width: 60px;
            }
        """)

    def add_button(self, text, tooltip=None, icon=None):
        """Добавляет кнопку на панель."""
        btn = QPushButton(text)
        self.dictBtn[text] = btn
        if tooltip:
            btn.setToolTip(tooltip)
        if icon:
            btn.setIcon(icon)
        btn.clicked.connect(lambda: self.buttonClicked.emit(text))
        self.layout.addWidget(btn)
        return btn

    def add_stretch(self):
        """Добавляет растягивающееся пространство."""
        self.layout.addStretch()
    def styleAll(self,style):
        setStyleBtns(self.dictBtn.values(),style)


