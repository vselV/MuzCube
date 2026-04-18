from PyQt6.QtGui import QColor


def bright(color: QColor, factor: float) -> QColor:
    """
    Изменяет яркость цвета с сохранением оттенка.

    Args:
        color: Исходный цвет (QColor)
        factor: Коэффициент изменения яркости:
               - >1.0 - сделать светлее
               - 1.0 - без изменений
               - <1.0 - сделать темнее

    Returns:
        Новый QColor с измененной яркостью

    Raises:
        ValueError: Если factor <= 0
    """
    if factor <= 0:
        raise ValueError("Factor must be greater than 0")

    # Преобразуем в HSL (оттенок-насыщенность-яркость)
    h, s, l, a = color.getHslF()

    # Изменяем яркость с учетом границ [0, 1]
    new_lightness = min(max(l * factor, 0.0), 1.0)

    # Создаем новый цвет с тем же оттенком и насыщенностью
    adjusted_color = QColor.fromHslF(h, s, new_lightness, a)

    # Для крайне темных/светлых цветов корректируем насыщенность
    if new_lightness < 0.1:
        adjusted_color = QColor.fromHslF(h, s * 0.8, new_lightness, a)
    elif new_lightness > 0.9:
        adjusted_color = QColor.fromHslF(h, s * 0.8, new_lightness, a)

    return adjusted_color