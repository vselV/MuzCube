import reapy
from reapy import reascript_api as RPR

# Получаем активный MIDI-тайк
take = RPR.MIDIEditor_GetTake(RPR.MIDIEditor_GetActive())
if not take:
    raise Exception("MIDI редактор не открыт!")
tk = take
take = reapy.Take(take)  # Оборачиваем в объект Take

# Добавляем текстовую подпись к первой ноте
notes = take.notes
if not notes:
    raise Exception("Нот не найдено!")

# Выбираем первую ноту (можно изменить индекс)
target_note = notes[0]

# Создаем текстовое событие в позиции начала ноты
text_event = {
    "selected": False,
    "muted": False,
    "position": target_note.start,  # Время в секундах
    "type": "Text",  # Тип события - текст
    "text": "Ornament"  # Ваш текст
}

# Добавляем событие в тайк
#take.add_event(text_event)
print(RPR.MIDI_InsertTextSysexEvt(tk,False,False,0,0,"qqqqssssssssss",2024))
# Обновляем отображение
RPR.UpdateArrange()