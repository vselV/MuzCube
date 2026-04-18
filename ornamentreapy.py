import reapy
from reapy import reascript_api as RPR
import ctypes
import struct


def add_note_with_ornament():
    # Подключение к REAPER
    if not reapy.is_inside_reaper():
        reapy.connect()

    # Получаем MIDI редактор
    midi_editor = RPR.MIDIEditor_GetActive()
    if not midi_editor:
        raise RuntimeError("MIDI Editor не открыт!")

    take = RPR.MIDIEditor_GetTake(midi_editor)
    if not take:
        raise RuntimeError("Не удалось получить MIDI take")

    # Параметры ноты
    note_pos = 0.0
    note_end = 1000
    note_chan = 0
    note_pitch = 60  # C4
    note_vel = 100

    # Добавляем ноту
    RPR.MIDI_InsertNote(
        take, False, False,
        note_pos, note_end,
        note_chan, note_pitch, note_vel,
        False
    )

    # Получаем позицию в PPQ

    ppq_pos = int(RPR.MIDI_GetPPQPosFromProjTime(take, note_pos))

    # Формируем текст события в правильном формате
    text_content = f"NOTE {note_chan} {note_pitch} text root"

    # Преобразуем строку в бинарный формат
    text_binary = text_content.encode('utf-8')
    text_length = len(text_binary)

    # Создаем ctypes буфер
    buf = ctypes.create_string_buffer(text_binary)

    # Вставляем текстовое событие
    success = RPR.MIDI_InsertTextSysexEvt(
        take,
        False,
        False,  # noSort
        ppq_pos,  # позиция
        15,  # тип события (15 = REAPER-specific)
        text_content,  # бинарные данные
        text_length,  # длина данных
    )
    '''
    success = RPR.MIDI_InsertTextSysexEvt(
        take,
        False,  # noSort
        ppq_pos,  # позиция
        15,  # тип события (15 = REAPER-specific)
        buf,  # бинарные данные
        text_length,  # длина данных
        0  # флаги
    )
'''
    if not success:
        print("Не удалось добавить текстовое событие")
    else:
        RPR.MIDI_Sort(take)
        print("Нота и текстовое украшение успешно добавлены!")


add_note_with_ornament()