import reapy
from reapy import reascript_api as RPR


def add_midi_file_to_track(track, midi_file_path, start_time_ticks, ticks_per_quarter=960):
    """
    Добавляет MIDI-файл на указанный трек в заданное время (в MIDI-тиках)

    :param track: Объект трека в REAPER
    :param midi_file_path: Путь к MIDI-файлу
    :param start_time_ticks: Время начала в MIDI-тиках (1 четверть = 960 тиков)
    :param ticks_per_quarter: Количество тиков в четвертной ноте (по умолчанию 960)
    """
    # Получаем текущий проект
    project = reapy.Project()

    # Конвертируем тики в секунды (предполагаем темп 120 BPM для расчета)
    # Можно изменить на текущий темп проекта, если нужно
    tempo = 120  # BPM
    seconds_per_quarter = 60.0 / tempo
    ticks_per_second = ticks_per_quarter / seconds_per_quarter
    start_time_seconds = start_time_ticks / ticks_per_second

    # Добавляем MIDI-файл на трек
    item = track.add_midi_item(start_time_seconds, start_time_seconds + 1)  # Длительность временно 1 сек

    # Получаем MIDI-события из файла
    take = item.active_take
    take.set_midi_file(midi_file_path)

    # Устанавливаем правильную длину айтема на основе MIDI-файла
    source = take.source
    midi_length_seconds = source.length
    item.set_info_value("D_LENGTH", start_time_seconds + midi_length_seconds)

    return item


# Пример использования
if __name__ == "__main__":
    # Подключаемся к REAPER
    reapy.update_reapy_config()

    # Получаем первый трек в проекте (можно изменить на нужный вам трек)
    project = reapy.Project()
    track = project.tracks[0]  # Или используйте project.selected_tracks[0] для выделенного трека

    # Параметры
    midi_file_path = "C:/path/to/your/file.mid"  # Укажите правильный путь
    start_time_ticks = 960  # Начинаем на 2-й четверти (если 1-я четверть = 0-960 тиков)

    # Добавляем MIDI-файл
    add_midi_file_to_track(track, midi_file_path, start_time_ticks)