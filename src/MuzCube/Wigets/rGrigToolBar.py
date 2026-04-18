from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QFrame,
                             QToolButton, QSizePolicy, QLabel, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QFont
import os


class ToolbarItem(QToolButton):
    """Элемент тулбара - может быть иконкой или текстом"""
  #  clicked = pyqtSignal()

    def __init__(self, icon_path=None, text="", size=32, is_toggle=False, parent=None):
        super().__init__(parent)

        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.font_f = QFont("Segoe UI Symbol")
       # self.font_f.setPointSize(13)
        self.font_f.setPixelSize(int(size/2.2))
        self.setFont(self.font_f)

        self.is_toggle = is_toggle
        self.size = size
        self.icon_path = icon_path
        self.text = text
        self.is_checked = False

        self.check_set = False

        self.style_no_toggle = """
                QToolButton {
                    background-color: #d0d0d0;
                    border: 1px solid #a0a0a0;
                    border-radius: 2px;
                    color: #606060;
                    font-weight: bold;
                    padding: 0px;
                    margin: 0px;
                }
                QToolButton:checked {
                    background-color: #a0c0ff;
                    border: 1px solid #8080ff;
                    color: #000000;
                }
                QToolButton:hover {
                    background-color: #c0c0c0;
                }
            """
        self.style_toggle = """
                QToolButton {
                    background-color: #e0e0e0;
                    border: 1px solid #b0b0b0;
                    border-radius: 2px;
                    color: #000000;
                    font-weight: bold;
                    padding: 0px;
                    margin: 0px;
                }
                QToolButton:pressed {
                    background-color: #c0c0c0;
                }
                QToolButton:hover {
                    background-color: #d0d0d0;
                }
            """
        self.links = None

        if is_toggle:
            self.setCheckable(True)
            self.toggled.connect(self._on_toggled)
        if icon_path and os.path.exists(icon_path):
            self.set_icon(icon_path)
        elif text:
            self.set_text(text)
    def set_links(self,items):
        self.links = items
        self.clicked.connect(self._update_links)
    def set_style_off(self,style):
        self.style_no_toggle = style
        self._update_appearance()
    def set_style_toggle(self,style):
        self.style_toggle = style
        self._update_appearance()
    def set_icon(self, icon_path):
        """Установить иконку из файла"""
        self.icon_path = icon_path
        self.text = ""
        self.original_pixmap = QPixmap(icon_path)
        self._update_appearance()

    def set_text(self, text):
        """Установить текст вместо иконки"""
        self.text = text
        self.icon_path = None
        self._update_appearance()

    def _update_appearance(self):
        """Обновить отображение элемента"""
        if self.icon_path and hasattr(self, 'original_pixmap'):
            self._update_icon()
        elif self.text:
            self._update_text()

    def _update_icon(self):
        """Обновить отображение иконки"""
        scaled_pixmap = self.original_pixmap.scaled(
            self.size - 6, self.size - 6,  # Уменьшил отступ для большей плотности
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # Создаем затемненную версию для выключенного состояния
        if self.is_toggle and not self.is_checked:
            dark_pixmap = QPixmap(scaled_pixmap.size())
            dark_pixmap.fill(Qt.GlobalColor.transparent)

            painter = QPainter(dark_pixmap)
            painter.setOpacity(0.5)  # Затемнение
            painter.drawPixmap(0, 0, scaled_pixmap)
            painter.end()

            self.setIcon(QIcon(dark_pixmap))
        else:
            self.setIcon(QIcon(scaled_pixmap))

        self.setText("")

    def _update_text(self):
        """Обновить отображение текста"""
        self.setIcon(QIcon())
        self.setText(self.text)

    def _on_toggled(self, checked):
        """Обработчик переключения"""
        self.is_checked = checked
        self._update_appearance()
    def _on_clicked(self):
        """Обработчик клика"""
        self.clicked.emit()
    def _update_links(self):
        if self.links is not None:
            if self.is_checked:
                for link in self.links:
                    if link != self:
                        link.setChecked(False)
            else:
                self.check_set = True
                self.setChecked(True)

    def out_toggle(self,checked):
        self.is_checked = checked
        self._update_appearance()

    def setChecked(self, checked):
        """Установить состояние checked"""
        if self.is_toggle:
            super().setChecked(checked)
            self.is_checked = checked
            self._update_appearance()


class DividerWidget(QFrame):
    """Разделитель между отделами тулбара"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setLineWidth(1)
        self.setFixedWidth(2)  # Уже разделитель
        self.setStyleSheet("""
            background-color: #aaaaaa; 
            margin: 4px 2px;
        """)


class ToolbarSection(QWidget):
    """Отдел тулбара с плотной сеткой иконок"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.no_snap()

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(1)  # Минимальный промежуток между иконками
        self.grid_layout.setContentsMargins(1, 1, 1, 1)  # Минимальные отступы
        self.setLayout(self.grid_layout)
       # self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.items = {}  # Словарь для хранения элементов по координатам
        self.current_row = 0
        self.current_col = 0
        self.max_cols = 4  # Максимальное количество колонок по умолчанию

       # self.grid_layout.setSizeConstraint(QGridLayout.SizeConstraint.SetFixedSize)
      #  self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        #self.set_vertical_alignment()

    def no_snap(self):
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    def add_item(self, item, row=None, col=None, tooltip=""):
        """Добавить элемент в указанную позицию"""
        if row is None:
            row = self.current_row
        if col is None:
            col = self.current_col

        if tooltip:
            item.setToolTip(tooltip)

        self.grid_layout.addWidget(item, row, col)
        self.items[(row, col)] = item

        # Обновляем текущую позицию для следующего элемента
        self.current_col += 1
        if self.current_col >= self.max_cols:
            self.current_col = 0
            self.current_row += 1

        return item


    def set_max_columns(self, max_cols):
        """Установить максимальное количество колонок"""
        self.max_cols = max_cols

    def clear(self):
        """Очистить отдел"""
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.items.clear()
        self.current_row = 0
        self.current_col = 0

    def set_vertical_alignment(self, align_top=True):
        """Установить выравнивание по верху или центру"""
        for row in range(self.grid_layout.rowCount()):
            self.grid_layout.setRowStretch(row, 0)
            if align_top:
                self.grid_layout.setRowMinimumHeight(row, 0)

class CustomToolBar(QWidget):
    """Кастомный тулбар с плотной сеточной организацией"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.main_layout = QHBoxLayout()
        self.main_layout.setSpacing(2)  # Уменьшил промежуток между отделами
        self.main_layout.setContentsMargins(2, 2, 2, 2)  # Минимальные отступы

        self.setLayout(self.main_layout)
        self.setStyleSheet("""
            CustomToolBar {
                background-color: #e8e8e8;
                border: 1px solid #b0b0b0;
                border-radius: 3px;
                padding: 1px;
            }
        """)

        self.sections = []  # Список отделов
        self._create_new_section()

    def _create_new_section(self,alignment = Qt.AlignmentFlag.AlignTop):
        """Создать новый отдел"""
        section = ToolbarSection()
        self.main_layout.addWidget(section,alignment=alignment)
        self.sections.append(section)
        return section

    def add_item(self, icon_path=None, text="", size=32, is_toggle=False,
                 tooltip="", row=None, col=None, section_index=None,alignment = Qt.AlignmentFlag.AlignTop):
        """Добавить элемент в указанный отдел и позицию"""
        if section_index is None:
            section_index = len(self.sections) - 1

        # Если указанного отдела нет, создаем его
        while section_index >= len(self.sections):
            self._create_new_section(alignment=alignment)

        section = self.sections[section_index]
        item = ToolbarItem(icon_path, text, size, is_toggle)
        section.add_item(item, row, col, tooltip)

        return item

    def add_separator(self):
        """Добавить разделитель между отделами"""
        separator = DividerWidget()
        self.main_layout.addWidget(separator)
        self._create_new_section()  # Создаем новый отдел после разделителя
        return separator

    def get_section(self, index):
        """Получить отдел по индексу"""
        if 0 <= index < len(self.sections):
            return self.sections[index]
        return None

    def set_section_columns(self, section_index, max_cols):
        """Установить количество колонок для отдела"""
        section = self.get_section(section_index)
        if section:
            section.set_max_columns(max_cols)

    def clear_section(self, section_index):
        """Очистить указанный отдел"""
        section = self.get_section(section_index)
        if section:
            section.clear()

    def clear(self):
        """Очистить весь тулбар"""
        for i in reversed(range(self.main_layout.count())):
            widget = self.main_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.sections = []
        self._create_new_section()
class PlayToolBar(CustomToolBar):
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self._setup_toolbar()

    def _setup_toolbar(self):
        # Отдел 1: Файловые операции (5 колонок - плотнее)
        self.set_section_columns(0, 4)
        size = 40
        self.play = self.add_item(text="▶", size=size, tooltip="play", is_toggle=True, row=0, col=0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.stop = self.add_item(text="||", size=size, tooltip="stop", is_toggle=True, row=0, col=1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.ret = self.add_item(text="◼", size=size, tooltip="return", row=0, col=2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.loop = self.add_item(text="↺", size=size, tooltip="loop", is_toggle=True, row=0, col=3,alignment=Qt.AlignmentFlag.AlignCenter)

       # self.stop.setChecked(True)
        self.play.clicked.connect(self.play_def)
        self.stop.clicked.connect(self.stop_def)
        self.ret.clicked.connect(self.return_def)
        self.loop.clicked.connect(self.loped)
        self.stop.setChecked(True)
       # self.loop.clicked.connect(self.editor.change_loop)
    def play_def(self):
        self.play.setChecked(True)
        self.stop.setChecked(False)

        self.editor.toggle_animation()
        self.editor.play_midi()
    def stop_def(self):
        a=self.play.is_checked
        self.play.setChecked(not a)
        self.stop.setChecked(a)


        self.editor.stop_animation()
        self.editor.stop_midi()
    def return_def(self):

        self.play.setChecked(False)
        self.stop.setChecked(False)

        self.editor.stop_ret()
        self.editor.stop_midi()

    def loped(self):
        self.editor.active_loop = self.loop.is_checked
def set_links_it(links):
    for link in links:
        link.set_links(links)
class TopTollBar(CustomToolBar):
    def __init__(self, editor, size = 20, parent=None):
        super().__init__(parent)
        self.size_ev = size
        self.editor = editor
        self.bind = self.editor.scene.mouse_key_manage
        self.hs_bol = True
        self.vs_bol = True
        self._setup_toolbar()

    def _setup_toolbar(self):
        # Отдел 1: Файловые операции (5 колонок - плотнее)
        size = self.size_ev
        ct = 0
        self.set_section_columns(ct, 1)
        self.remove = self.add_item(text="❌", size=size, tooltip="remove", is_toggle=True, row=0, col=0)
        self.select = self.add_item(text="⏍", size=size, tooltip="selection", is_toggle=True, row=1, col=0)
        set_links_it([self.select, self.remove])
        self.remove.setChecked(True)
        print(self.bind.set_flag)
        self.remove.clicked.connect(lambda: self.bind.set_flag("delete"))
        self.select.clicked.connect(lambda: self.bind.set_flag("select"))
        self.add_separator()
        ct+=1
        self.set_section_columns(ct, 1)
        self.draw = self.add_item(text="🖌", size=size, tooltip="drawing", is_toggle=True, row=0, col=0)
        self.fill = self.add_item(text="_", size=size, tooltip="fill", is_toggle=True, row=1, col=0)
        set_links_it([self.draw, self.fill])
        self.draw.setChecked(True)
        self.draw.clicked.connect(lambda: self.bind.set_flag("draw"))
        self.fill.clicked.connect(lambda: self.bind.set_flag("fill"))
        self.add_separator()
        ct+=1
        self.set_section_columns(ct, 2)
        self.h_vis = self.add_item(text="—👁", size=size, tooltip="grid visible", is_toggle=True, row=0, col=0)
        self.v_vis = self.add_item(text="|👁", size=size, tooltip="grid visible", is_toggle=True, row=0, col=1)
        self.h_snap = self.add_item(text="—⚓", size=size, tooltip="grid snap", is_toggle=True, row=1, col=0)
        self.v_snap = self.add_item(text="|⚓", size=size, tooltip="grid snap", is_toggle=True, row=1, col=1)
        self.add_separator()
        ct+=1
        self.set_section_columns(ct, 1)
        self.tracks = self.add_item(text="⍈", size=size, tooltip="tracks", is_toggle=True, row=0, col=0)
        self.loped = self.add_item(text="''", size=size, tooltip="loop", is_toggle=True, row=0, col=1)
        self.events_synk = self.add_item(text="e", size=size, tooltip="events sync", is_toggle=True, row=1, col=0)
        self.events_synk = self.add_item(text="~", size=size, tooltip="events sync", is_toggle=True, row=1, col=1)

        self.h_vis.setChecked(True)
        self.v_vis.setChecked(True)
        self.h_snap.setChecked(True)
        self.v_snap.setChecked(True)

        self.h_vis.clicked.connect(self.h_vis_def)
        self.v_vis.clicked.connect(self.v_vis_def)
    def h_vis_def(self):
        if not self.h_vis.isChecked():
            self.hs_bol = self.h_snap.isChecked()
            self.h_snap.setChecked(False)
        else:
            self.h_snap.setChecked(self.hs_bol)
    def v_vis_def(self):
        if not self.v_vis.isChecked():
            self.vs_bol = self.v_snap.isChecked()
            self.v_snap.setChecked(False)
        else:
            self.v_snap.setChecked(self.vs_bol)
#        self.strike_btn.clicked.connect(self.on_strike_toggled)
# Пример использования с плотным расположением
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit


    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Custom Toolbar with Compact Grid Layout")
            self.setGeometry(100, 100, 800, 500)

            # Создаем центральный виджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # Создаем основной layout
            main_layout = QVBoxLayout(central_widget)
            main_layout.setSpacing(2)
            main_layout.setContentsMargins(2, 2, 2, 2)

            # Создаем кастомный тулбар
            self.toolbar = CustomToolBar()
            main_layout.addWidget(self.toolbar)

            # Добавляем текстовый редактор
            self.text_edit = QTextEdit()
            main_layout.addWidget(self.text_edit)

            # Настраиваем тулбар
            self._setup_toolbar()

        def _setup_toolbar(self):
            # Отдел 1: Файловые операции (5 колонок - плотнее)
            self.toolbar.set_section_columns(0, 5)

            self.toolbar.add_item(text="New", size=28, tooltip="Новый файл", row=0, col=0)
            self.toolbar.add_item(text="Open", size=28, tooltip="Открыть", row=0, col=1)
            self.toolbar.add_item(text="Save", size=28, tooltip="Сохранить", row=0, col=2)
            self.toolbar.add_item(text="Export", size=28, tooltip="Экспорт", row=0, col=3)
            self.toolbar.add_item(text="Print", size=28, tooltip="Печать", row=0, col=4)

            # Разделитель
            self.toolbar.add_separator()

            # Отдел 2: Форматирование (4 колонки)
            self.toolbar.set_section_columns(1, 4)

            self.bold_btn = self.toolbar.add_item(text="B", size=28, is_toggle=True,
                                                  tooltip="Жирный", row=0, col=0, section_index=1)
            self.italic_btn = self.toolbar.add_item(text="I", size=28, is_toggle=True,
                                                    tooltip="Курсив", row=0, col=1, section_index=1)
            self.underline_btn = self.toolbar.add_item(text="U", size=28, is_toggle=True,
                                                       tooltip="Подчеркивание", row=0, col=2, section_index=1)
            self.strike_btn = self.toolbar.add_item(text="S", size=500, is_toggle=True,
                                                    tooltip="Зачеркивание", row=0, col=3, section_index=1)

            # Еще один разделитель
            self.toolbar.add_separator()

            # Отдел 3: Выравнивание (4 колонки)
            self.toolbar.set_section_columns(2, 4)

            self.toolbar.add_item(text="←", size=28, tooltip="По левому краю", row=0, col=0, section_index=2)
            self.toolbar.add_item(text="→", size=28, tooltip="По правому краю", row=0, col=1, section_index=2)
            self.toolbar.add_item(text="↔", size=28, tooltip="По центру", row=0, col=2, section_index=2)
            self.toolbar.add_item(text="⇄", size=28, tooltip="По ширине", row=0, col=3, section_index=2)

            # Отдел 4: Цвета (3 колонки в 2 ряда)
            self.toolbar.set_section_columns(3, 3)

            self.toolbar.add_item(text="🔴", size=24, tooltip="Красный", row=0, col=0, section_index=3)
            self.toolbar.add_item(text="🔵", size=24, tooltip="Синий", row=0, col=1, section_index=3)
            self.toolbar.add_item(text="🟢", size=24, tooltip="Зеленый", row=0, col=2, section_index=3)
            self.toolbar.add_item(text="🟡", size=24, tooltip="Желтый", row=1, col=0, section_index=3)
            self.toolbar.add_item(text="🟣", size=24, tooltip="Фиолетовый", row=1, col=1, section_index=3)
            self.toolbar.add_item(text="⚫", size=24, tooltip="Черный", row=1, col=2, section_index=3)

            # Подключаем сигналы
            self.bold_btn.clicked.connect(self.on_bold_toggled)
            self.italic_btn.clicked.connect(self.on_italic_toggled)
            self.underline_btn.clicked.connect(self.on_underline_toggled)
            self.strike_btn.clicked.connect(self.on_strike_toggled)

        def on_bold_toggled(self):
            self.text_edit.append(f"Жирный: {self.bold_btn.isChecked()}")

        def on_italic_toggled(self):
            self.text_edit.append(f"Курсив: {self.italic_btn.isChecked()}")

        def on_underline_toggled(self):
            self.text_edit.append(f"Подчеркивание: {self.underline_btn.isChecked()}")

        def on_strike_toggled(self):
            self.text_edit.append(f"Зачеркивание: {self.strike_btn.isChecked()}")


    app = QApplication(sys.argv)
   # window  = MainWindow()
   # window = PlayToolBar(None)
    window = TopTollBar(None)
    window.show()
    sys.exit(app.exec())