from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtCore import QFile, QFileInfo
import os


def safe_add_application_font(font_path):
    """Безопасная загрузка шрифта"""
    try:
        # Проверяем существование файла
        if not os.path.exists(font_path):
            print(f"Font file not found: {font_path}")
            return None

        # Проверяем права доступа
        if not os.access(font_path, os.R_OK):
            print(f"No read access to font file: {font_path}")
            return None

        # Загружаем через QFile для безопасности
        font_file = QFile(font_path)
        if not font_file.open(QFile.OpenModeFlag.ReadOnly):
            print(f"Cannot open font file: {font_path}")
            return None

        # Получаем данные шрифта
        font_data = font_file.readAll()
        font_file.close()

        if font_data.isEmpty():
            print(f"Font file is empty: {font_path}")
            return None
        print("a")

        # Добавляем шрифт из данных
        font_id = QFontDatabase.addApplicationFontFromData(font_data)
        print("b")

        if font_id == -1:
            print(f"Failed to add font: {font_path}")
            return None

        # Получаем имя семейства шрифтов
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if not font_families:
            print(f"No font families found in: {font_path}")
            return None

        print(f"Successfully loaded font: {font_families[0]}")
        return font_families[0]

    except Exception as e:
        print(f"Error loading font {font_path}: {e}")
        return None


# Использование
font_family = safe_add_application_font("./Symbola.ttf")
if font_family:
    font = QFont(font_family, 12)
else:
    # Fallback на системный шрифт
    font = QFont("Segoe UI Symbol", 12)