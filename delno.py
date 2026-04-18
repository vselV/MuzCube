import reapy
from reapy import reascript_api as RPR

# Получаем текущий проект
project = reapy.Project()

take = RPR.MIDIEditor_GetTake(RPR.MIDIEditor_GetActive())
take = reapy.Take(take)

# Получаем все ноты
notes = take.notes

if notes:
    # Удаляем первую ноту (пример: note_index = 0)
    print(notes[0].pitch)
    print(notes[0].text)
    RPR.MIDI_DeleteNote(take.id, notes[0].index)
  #  take.delete_note(notes[0].index)  # или явно указать индекс note_id