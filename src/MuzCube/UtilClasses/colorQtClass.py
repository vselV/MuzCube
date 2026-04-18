from PyQt6.QtGui import QTextCharFormat, QColor
from pygments.token import Token
from collections import defaultdict

from pygments.styles import get_style_by_name, get_all_styles
from pygments.style import Style
from typing import Type

from pygments.util import ClassNotFound
from src.MuzCube.UtilFIles import dataTok


def get_pygments_style(style_name: str) -> Type[Style]:
    """
    Получает класс стиля Pygments по имени.

    Args:
        style_name: Название стиля (например 'monokai', 'friendly')

    Returns:
        Класс стиля (наследник pygments.style.Style)

    Raises:
        ValueError: Если стиль с таким именем не найден
    """
    try:
        return get_style_by_name(style_name)
    except ClassNotFound:
        available_styles = ", ".join(get_all_styles())
        raise ValueError(
            f"Стиль '{style_name}' не найден. Доступные стили: {available_styles}"
        ) from None
def onestyle(str,fmt):
    parts = str.split(" ")
    for part in parts:
        if part.startswith('#'):
            fmt.setForeground(QColor(part))
        elif part == 'bold':
            fmt.setFontWeight(75)
        elif part == 'nobold':
            fmt.setFontWeight(50)
        elif part == 'italic':
            fmt.setFontItalic(True)
        elif part == 'noitalic':
            fmt.setFontItalic(False)
        elif part == 'underline':
            fmt.setFontUnderline(True)
        elif part == 'nounderline':
            fmt.setFontUnderline(False)
def rec_token(style,dict):
    for key in dataTok.STANDARD_TYPES_SP.keys():
        mass = [key]
        tok = key.parent
        while tok is not None and not "noinherit" in style.get(mass[0],""):
            mass.append(tok)
            tok = tok.parent
        fmt = QTextCharFormat()
        for item in reversed(mass):
            onestyle(style.get(item,""),fmt)
        dict[key] = fmt

def create_style_dict(style_class):
    """
    Создает полный словарь стилей с учетом всех особенностей Pygments.

    Args:
        style_class: Класс стиля Pygments (наследник pygments.style.Style)

    Returns:
        Словарь вида {
            Token: QTextCharFormat,
            'background': QColor,
            'selected': QColor,
            'global': {
                'bg': QColor,
                'border': QColor
            }
        }
    """
    style_dict = {
        'background': QColor('#1e1e1e'),
        'background_st': '#1e1e1e',
        'selected': QColor('#264F78'),
        'selected_st': '#264F78',
        'global': {
            'bg': None,
            'border': None
        }
    }

    # Создаем экземпляр стиля и получаем его атрибуты
    style = style_class()

    # Обрабатываем глобальные атрибуты
    if hasattr(style, 'background_color'):
        style_dict['background'] = QColor(style.background_color)
        style_dict['background_st'] = style.background_color

    if hasattr(style, 'highlight_color'):
        style_dict['selected'] = QColor(style.highlight_color)
        style_dict['selected_st'] = style.highlight_color

    # Словарь для хранения "noinherit" токенов
    if not hasattr(style_class, 'styles'):
        return style_dict

    style = style_class()
    styles = getattr(style, 'styles', {})

    # Обработка всех токенов из стиля
    for token, style_def in styles.items():
        if not isinstance(style_def, str):
            continue

        fmt = QTextCharFormat()
        parts = style_def.split()
        bg_color = None
        border_color = None
        noinherit = False

        for part in parts:
            if part.startswith('#'):
                fmt.setForeground(QColor(part))
            elif part.startswith('bg:#'):
                bg_color = QColor(part[4:])
            elif part.startswith('border:#'):
                border_color = QColor(part[8:])
            elif part == 'bold':
                fmt.setFontWeight(75)
            elif part == 'nobold':
                fmt.setFontWeight(50)
            elif part == 'italic':
                fmt.setFontItalic(True)
            elif part == 'noitalic':
                fmt.setFontItalic(False)
            elif part == 'underline':
                fmt.setUnderlineStyle(1)
            elif part == 'nounderline':
                fmt.setUnderlineStyle(0)
            elif part == 'noinherit':
                noinherit = True

        style_dict[token] = {
            'format': fmt,
            'bg': bg_color,
            'border': border_color,
            'noinherit': noinherit
        }

    # Обработка наследования
    token_hierarchy = defaultdict(list)

    # Строим иерархию наследования
    for token in styles.keys():
        parent = token.parent
        while parent is not None:
            token_hierarchy[parent].append(token)
            parent = parent.parent

    # Применяем наследование
    for parent_token, child_tokens in token_hierarchy.items():
        if parent_token not in style_dict:
            continue

        if style_dict[parent_token].get('noinherit'):
            continue

        parent_style = style_dict[parent_token]

        for child_token in child_tokens:
            if child_token not in style_dict:
                # Создаем новый формат на основе родительского
                child_fmt = QTextCharFormat(parent_style['format'])
                style_dict[child_token] = {
                    'format': child_fmt,
                    'bg': parent_style['bg'],
                    'border': parent_style['border'],
                    'noinherit': False
                }

    # Устанавливаем стиль по умолчанию
    if Token.Text not in style_dict:
        default_fmt = QTextCharFormat()
        default_fmt.setForeground(QColor('#d4d4d4'))
        style_dict[Token.Text] = {
            'format': default_fmt,
            'bg': None,
            'border': None,
            'noinherit': False
        }
  #  print(style_dict)
    for token in style_dict.keys():
        if type(token) is not str:
    #        print(token)
            style_dict[token] = style_dict[token]["format"]
  #  print(style_dict)
    return style_dict
def my_create_stile(style_class):
    style_dict = {
        'background': QColor('#1e1e1e'),
        'background_st': '#1e1e1e',
        'selected': QColor('#264F78'),
        'selected_st': '#264F78',
        'global': {
            'bg': None,
            'border': None
        }
    }

    # Создаем экземпляр стиля и получаем его атрибуты
    style = style_class()

    # Обрабатываем глобальные атрибуты
    if hasattr(style, 'background_color'):
        style_dict['background'] = QColor(style.background_color)
        style_dict['background_st'] = style.background_color

    if hasattr(style, 'highlight_color'):
        style_dict['selected'] = QColor(style.highlight_color)
        style_dict['selected_st'] = style.highlight_color
    style = style_class()
    styles = getattr(style, 'styles', {})
    rec_token(styles,style_dict)
    return style_dict
def by_name_dict(name):
    return my_create_stile(get_pygments_style(name))