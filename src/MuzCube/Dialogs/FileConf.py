from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QLabel, QCheckBox, QLineEdit, QComboBox,
                             QPushButton, QDialog)
from src.MuzCube.UtilClasses.FileDict import FileDict


class SettingsDialog(QDialog):
    def __init__(self, parent=None, config_file="settings.txt",**kwargs):
        super().__init__(parent)
        if kwargs.get("dict") is not None:
            self.config = kwargs.get("dict")
        else:
            self.config = FileDict(config_file)
        
        self.setup_ui()

        # Структура настроек (группы и параметры)
        self.settings_structure = kwargs.get("struct",{
            "Общие": {
                "theme": {"type": "combobox", "values": ["light", "dark", "system"], "default": "light"},
                "language": {"type": "combobox", "values": ["ru", "en"], "default": "ru"},
                "auto_save": {"type": "checkbox", "default": True}
            },
            "Редактор": {
                "font_size": {"type": "entry", "default": "12"},
                "show_line_numbers": {"type": "checkbox", "default": True},
                "tab_width": {"type": "combobox", "values": ["2", "4", "8"], "default": "4"}
            }
        })

        self.create_tabs()
        self.load_settings()

    def setup_ui(self):
        self.setWindowTitle("Настройки")
        self.setFixedSize(500, 400)

        self.main_layout = QVBoxLayout(self)

        # Создаем вкладки
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        # Кнопки сохранения/отмены
        self.button_box = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")

        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn.clicked.connect(self.close)

        self.button_box.addStretch()
        self.button_box.addWidget(self.save_btn)
        self.button_box.addWidget(self.cancel_btn)

        self.main_layout.addLayout(self.button_box)

    def create_tabs(self):
        """Создает вкладки с настройками"""
        for tab_name, settings in self.settings_structure.items():
            tab = QWidget()
            layout = QVBoxLayout(tab)

            for setting_name, params in settings.items():
                # Создаем строку с настройкой
                row = QHBoxLayout()

                # Название параметра
                label = QLabel(setting_name)
                row.addWidget(label)

                # Виджет в зависимости от типа
                if params["type"] == "checkbox":
                    widget = QCheckBox()
                    params["widget"] = widget
                elif params["type"] == "combobox":
                    widget = QComboBox()
                    widget.addItems(params["values"])
                    params["widget"] = widget
                else:  # entry по умолчанию
                    widget = QLineEdit()
                    params["widget"] = widget

                row.addWidget(widget)
                layout.addLayout(row)

            layout.addStretch()
            self.tab_widget.addTab(tab, tab_name)

    def load_settings(self):
        """Загружает текущие значения настроек"""
        for tab_name, settings in self.settings_structure.items():
            for setting_name, params in settings.items():
                value = self.config.get(setting_name, params["default"])
                widget = params["widget"]

                if isinstance(widget, QCheckBox):
                    widget.setChecked(str(value).lower() == "true" if isinstance(value, str) else bool(value))
                elif isinstance(widget, QComboBox):
                    index = widget.findText(value)
                    if index >= 0:
                        widget.setCurrentIndex(index)
                else:  # QLineEdit
                    widget.setText(str(value))

    def save_settings(self):
        """Сохраняет настройки в конфиг"""
        for tab_name, settings in self.settings_structure.items():
            for setting_name, params in settings.items():
                widget = params["widget"]

                if isinstance(widget, QCheckBox):
                    value = widget.isChecked()
                elif isinstance(widget, QComboBox):
                    value = widget.currentText()
                else:  # QLineEdit
                    value = widget.text()

                self.config[setting_name] = str(value)

        self.accept()
        print("Настройки сохранены:", self.config)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Главное окно")
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.settings_btn = QPushButton("Открыть настройки")
        self.settings_btn.clicked.connect(self.show_settings)
        layout.addWidget(self.settings_btn)

        self.settings_dialog = None

    def show_settings(self):
        """Показывает окно настроек"""
        if self.settings_dialog is None or not self.settings_dialog.isVisible():
            self.settings_dialog = SettingsDialog(self)
            self.settings_dialog.finished.connect(self.on_settings_closed)
            self.settings_dialog.show()

    def on_settings_closed(self, result):
        """Обработчик закрытия окна настроек"""
        if result == QDialog.DialogCode.Accepted:
            print("Настройки были сохранены")
        else:
            print("Изменения отменены")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()