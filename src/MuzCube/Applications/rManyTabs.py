from src.MuzCube.Scripts import recolor, rUtils
from src.MuzCube.UtilClasses.FileDict import FileDict
from src.MuzCube.Lex.filnalDepLexWin import *
import sys
import os
from PyQt6.QtWidgets import (QApplication, QPlainTextEdit, QWidget, QVBoxLayout,
                             QTabWidget, QFileDialog, QMenuBar, QMenu, QMessageBox,
                             QToolButton, QInputDialog, QLabel, QHBoxLayout, QPushButton, QDialog)
from PyQt6.QtGui import (QAction, QIcon, QPalette)
from PyQt6.QtCore import Qt
from src.MuzCube.UtilClasses import colorQtClass
from src.MuzCube.Wigets.rButtonPanel import ButtonPanel, setStyleBtns

import src.MuzCube.Lex.tomObj as tomObj
from midiutil import MIDIFile
import reapy
from src.MuzCube.Dialogs.FileConf import SettingsDialog
from MidiWidget import MidiPlayerWidget
import midiread

class SignatureWidget(QWidget):
    def __init__(self, text="Подпись автора", parent=None,bg="#f0f0f0",name="#606060"):
        super().__init__(parent)

        # Настройка виджета
        self.setFixedHeight(20)  # Фиксированная высота
        self.setStyleSheet(f"""
                   background-color:{bg};
                   border-top: 1px solid #d0d0d0;
               """)

        # Создаем подпись
        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.label.setStyleSheet("""
                   QLabel {
                       color: #606060;
                       font-style: italic;
                   }
               """)

        # Простой горизонтальный layout
        layout = QHBoxLayout()
       # layout.addStretch()  # Растягиваемое пространство слева
        layout.addWidget(self.label)
        self.setLayout(layout)

class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
    #    self.setFixedHeight(21)  # Высота шапки
        self.drag_start_position = None
        self.setup_ui()
    def setup_ui(self):


      #  self.setWindowFlags(Qt.WindowType.FramelessWindowHint)


        self.setFixedHeight(30)
        layout = QHBoxLayout(self)
        self.title_label = QLabel("MuzCube")
        layout.addWidget(self.title_label)
      #  layout.setFixedHeight(30)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(5)

        # Название окна
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Кнопки управления
        self.min_btn = QPushButton("—")
        self.max_btn = QPushButton("□")
        self.close_btn = QPushButton("✕")

        # Настройка кнопок
        for btn in [self.min_btn, self.max_btn, self.close_btn]:
            btn.setFixedSize(20, 20)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

        # Подключение событий
        self.close_btn.clicked.connect(self.window().close)
        self.min_btn.clicked.connect(self.window().showMinimized)
          #  self.max_btn.clicked.connect(self.toggle_maximize)

        # --- Функции для перетаскивания окна (PyQt6) ---
    def retext(self,text):
        if text != "":
            self.title_label.setText(" - "+text)
    def mousePressEvent(self, event):
        """Запоминаем позицию клика для перетаскивания."""
        if event.button() == Qt.MouseButton.LeftButton:  # Изменено для PyQt6
            self.drag_start_position = event.globalPosition().toPoint()  # Изменено для PyQt6

    def mouseMoveEvent(self, event):
        """Перемещаем окно при зажатой ЛКМ."""
        if event.buttons() & Qt.MouseButton.LeftButton and self.drag_start_position:  # Изменено для PyQt6
            delta = event.globalPosition().toPoint() - self.drag_start_position  # Изменено для PyQt6
            self.parent().move(self.parent().pos() + delta)
            self.drag_start_position = event.globalPosition().toPoint()  # Изменено для PyQt6

    def mouseReleaseEvent(self, event):
        """Сбрасываем позицию при отпускании кнопки."""
        if event.button() == Qt.MouseButton.LeftButton:  # Изменено для PyQt6
            self.drag_start_position = None
class CodeEditorTab(QPlainTextEdit):
    def __init__(self, file_path=None,**kwargs):
        super().__init__()

        self.file_path = file_path
        self.highlighter = None
        self.stylek = kwargs.get("style")
        self.pt = kwargs.get("font_size",13)
        self.setup_editor()

    def set_style(self,style):
        self.stylek = style
    def setup_editor(self):
        bg = '#1e1e1e'
        sel = '#264F78'
        if self.stylek is not None:
           # print(self.stylek)
            bg = self.stylek.get('background_st')
            sel = self.stylek.get('selected_st')
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

    def set_highlighter(self, highlighter):
        self.highlighter = highlighter(self.document(),style=self.stylek)


class TabbedCodeEditor(QWidget):
    def __init__(self,**kwargs):
        super().__init__()
        self.allThemes = open("themes.txt").read().split("\n")
        #self.setup_custom_window_buttons()
        self.settings_file = "settings.txt"
        self.settings_dialog = None

        self.settings_dict = FileDict(self.settings_file)
        
        self.buttonDict = {}
        self.reaData = None
        self.reaCOn = False
        
        self.style = None
        self.sty = kwargs.get('style',)
        if self.sty is None:
            self.sty = self.settings_dict.get('style',"nord")
        self.chan_max = self.settings_dict.get("max channels reaper",4)
        self.settings_dict["style"] = self.sty
        self.bg="#1e1e1e"
        self.sel='#264F78'
        self.style = colorQtClass.by_name_dict(self.sty)
        self.bg = self.style.get('background')
        self.sel = self.style.get('selected')

       # self.setup_ui()



        self.setWindowTitle("MuzCube Editor")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint) ##########stokov
        self.title_bar = CustomTitleBar(self)
        self.layout.addWidget(self.title_bar)

        self.create_menu()
        self.create_tab_widget()
        self.add_new_tab()

        self.midi_player = MidiPlayerWidget()
        self.layout.addWidget(self.midi_player)
        self.current_midi = None

        self.button_panel = ButtonPanel(self)
        self.layout.addWidget(self.button_panel)
        self.button_panel.add_button("Run", "Запустить код")
        self.button_panel.add_button("Connect", "Присоедениться к Риперу")
        self.button_panel.add_button("Debug", "Отладка")
        self.button_panel.add_stretch()  # Растягивающееся пространство
        self.button_panel.add_button("Settings", "Настройки")

        self.window_colors()
        self.button_panel.buttonClicked.connect(self.on_button_clicked)

        self.setDefSettings_struct()
        self.simp_update()
    def on_settings_closed(self, result):
        """Обработчик закрытия окна настроек"""
        if result == QDialog.DialogCode.Accepted:
            print("Настройки были сохранены")
            self.update_settings()
        else:
            print("Изменения отменены")
    def simp_update(self):
        self.chan_max = int(self.settings_dict.get("max channels reaper", 4))
    def update_settings(self):
        if self.sty != self.settings_dict.get('style',"nord"):
            self.sty = self.settings_dict.get('style',"nord")
            self.style = colorQtClass.by_name_dict(self.sty)
            self.bg = self.style.get('background')
            self.sel = self.style.get('selected')
            self.window_colors()
            for i in range(self.tabs.count()):
                editor = self.tabs.widget(i)
                editor.set_style(self.style)
                editor.setup_editor()
                editor.set_highlighter(ContextAwareHighlighter)
        self.simp_update()

    def on_button_clicked(self, text):
        """Обработчик нажатий кнопок."""
        if text == "Run":
         #   print(1)
            self.runCurrent()
        elif text == "Connect":
            self.reaperCon()
        elif text == "Debug":
            print("Режим отладки...")
        elif text == "Settings":
            self.OpenSettings(self.settings_file)
            print("Открыть настройки...")
    def setDefSettings_struct(self):
        self.settins_struct = {
            "Общие": {
                "style": {"type": "combobox", "values": self.allThemes , "default": self.sty},
                "max channels reaper": {"type": "combobox", "values": list(map(str, range(1, 17))), "default": str(self.chan_max)}
            },
        }
    def OpenSettings(self,file):
        if self.settings_file == file:
            if self.settings_dialog is None or not self.settings_dialog.isVisible():
                self.settings_dialog = SettingsDialog(self,self.settings_file,dict = self.settings_dict, struct = self.settins_struct)
                self.settings_dialog.finished.connect(self.on_settings_closed)
                self.settings_dialog.show()
    def reaperCon(self):
        if not reapy.is_inside_reaper():
            if reapy.connect():
                self.title_bar.retext(reapy.Project().name)
                '''QMessageBox.information(
                    None,  # Родительское окно (None — без родителя)
                    "Успех",  # Заголовок
                    "REAPER подключён!"  # Текст
                )'''
                self.reaCon = True
    def runCurrent(self,**kwargs):
        file = self.get_current_editor().file_path
        strFile = str(file).replace("\\", "/")
        files = rUtils.getPaths(strFile)
     #   try:
        if kwargs.get("reapy", False):
            tomObj.toMidi(strFile, 0, MIDIFile(), reapyBol=True, reapyData=self.take, chanMax=self.chan_max)
        else:
            tomObj.toMidi(strFile, 0, MIDIFile())
     #   except:
       #     print(1)
        self.current_midi = midiread.midi_to_events(files[0])
        duration = midiread.get_midi_duration(files[0])
        self.midi_player.load_midi_data(self.current_midi,duration)
        ''' try:
                if kwargs.get("reapy",False):
                    tomObj.toMidi("f.txt", 0, MIDIFile(), reapyBol=True, reapyData=self.take, chanMax=4)
                midObj = tomObj.toMidi(strFile, 0, MIDIFile())
                strem = threading.Thread(target=toMidGa.start, args=(files[0],), daemon=True)
                strem.start()
            except:
                print(1)'''

    def window_colors(self):

        palette = self.palette()

        # Основные цвета (для QWidget)

        if self.style is not None:
            palette.setColor(QPalette.ColorRole.Window, recolor.bright(self.bg, 0.9))  # Фон виджета
            palette.setColor(QPalette.ColorRole.Base, self.bg)  # Фон полей ввода

            palette.setColor(QPalette.ColorRole.WindowText, recolor.bright(self.style.get(Token.Text).foreground().color(),1.2))  # Текст

            palette.setColor(QPalette.ColorRole.Text, recolor.bright(self.style.get(Token.Text).foreground().color(),1.2))  # Текст полей ввода
            palette.setColor(QPalette.ColorRole.Button, recolor.bright(self.style.get(Token.Comment).foreground().color(),0.9))  # Кнопки
            palette.setColor(QPalette.ColorRole.ButtonText,  self.style.get(Token.Name.Builtin).foreground().color())  # Текст кнопок
            self.btnStyle = f"""
                        QToolButton {{
                            background-color: {recolor.bright(self.style.get(Token.Comment).foreground().color(),0.9).name()}; 
                            color: {recolor.bright(self.style.get(Token.Name).foreground().color(),1.2).name()};
                        }}
                        QPushButton {{
                            background-color: {recolor.bright(self.style.get(Token.Comment).foreground().color(),0.9).name()};
                            color: {recolor.bright(self.style.get(Token.Name).foreground().color(),1.2).name()};
                        }}
                        QPushButton:hover {{
                            background-color: {self.style.get('button_hover', '#4a4a4a')};
                        }}
                    """
          #  self.setStyleSheet(self.btnStyle)
            self.button_panel.styleAll(self.btnStyle)
         #   print(self.buttonDict)
            self.button_col()
        # Применяем палитру
        self.setPalette(palette)
    def create_menu(self):
        menubar = QMenuBar(self)

        file_menu = QMenu("&File", self)

        color_menu = QMenu("&Color", self)

        new_action = QAction(QIcon(), "&New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.add_new_tab)

        open_action = QAction(QIcon(), "&Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)

        save_action = QAction(QIcon(), "&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)

        save_as_action = QAction(QIcon(), "Save &As", self)
        save_as_action.triggered.connect(self.save_file_as)

        exit_action = QAction(QIcon(), "E&xit", self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        menubar.addMenu(file_menu)
        menubar.addMenu(color_menu)
        self.layout.addWidget(menubar)

    def create_tab_widget(self):
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        # Добавляем кнопку "+" для новых вкладок
        add_tab_button = QToolButton()
        self.buttonDict["+"] = add_tab_button
        add_tab_button.setText('+')
        add_tab_button.setStyleSheet("""
            QToolButton {
                font-size: 16px;
                padding: 0px 4px;
            }
        """)
        add_tab_button.clicked.connect(self.add_new_tab)
        self.tabs.setCornerWidget(add_tab_button, Qt.Corner.TopRightCorner)

        self.layout.addWidget(self.tabs)

    def add_new_tab(self, file_path=None, content=""):
     #   print(file_path)
        if not file_path:

            file_name, ok = QInputDialog.getText(
                self,
                "Новый фаил",
                "Введите имя файла:",
                text=""
            )

            if not ok or not file_name:
                return
            # Создаем полный путь в папке проекта
            project_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(project_dir, file_name)

        editor = CodeEditorTab(file_path,style = self.style)
        editor.set_highlighter(ContextAwareHighlighter)

        if file_path and os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                editor.setPlainText(f.read())

        else:
            editor.setPlainText(content)
        tab_title = os.path.basename(file_path)

        self.tabs.addTab(editor, tab_title)
        self.tabs.setCurrentWidget(editor)
        editor.setFocus()

    def get_current_editor(self):
        return self.tabs.currentWidget()

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "All Files (*);;Python Files (*.py)")

        if file_path:
            for i in range(self.tabs.count()):
                editor = self.tabs.widget(i)
                if editor.file_path == file_path:
                    self.tabs.setCurrentIndex(i)
                    return

            self.add_new_tab(file_path)

    def save_file(self):
        editor = self.get_current_editor()
        if not editor:
            return

        if editor.file_path:
            self._save_to_file(editor.file_path, editor.toPlainText())
        else:
            self.save_file_as()

    def save_file_as(self):
        editor = self.get_current_editor()
        if not editor:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "All Files (*);;Python Files (*.py)")

        if file_path:
            self._save_to_file(file_path, editor.toPlainText())
            editor.file_path = file_path
            self.tabs.setTabText(self.tabs.currentIndex(), os.path.basename(file_path))

    def _save_to_file(self, file_path, content):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

    def close_tab(self, index):
        editor = self.tabs.widget(index)
        if editor.toPlainText() and not self._confirm_close():
            return

        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            self.add_new_tab()

    def _confirm_close(self):
        return QMessageBox.question(
            self, "Confirm Close",
            "You have unsaved changes. Close anyway?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes

    def closeEvent(self, event):
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if editor.toPlainText() and not editor.file_path:
                if not self._confirm_close():
                    event.ignore()
                    return

        super().closeEvent(event)
    def button_col(self):
        setStyleBtns(self.buttonDict.values(),self.btnStyle)

# Остальные классы (StateManager, AsyncLexer, ContextAwareHighlighter) остаются без изменений
# ...

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    editor = TabbedCodeEditor(style="nord")
    editor.show()
    sys.exit(app.exec())