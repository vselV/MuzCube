import reapy
from reapy import reascript_api as RPR
import src.MuzCube.Lex.tomObj
from midiutil import MIDIFile

# Проверка подключения
if not reapy.is_inside_reaper():
    reapy.connect()  # Подключение к Reaper
proj = reapy.Project()
#midi_editor = proj.midi_editor()
#take = midi_editor.get_active_midi_take()
take = RPR.MIDIEditor_GetTake(RPR.MIDIEditor_GetActive())
take = reapy.Take(take)
#a = tomObj.toMidi("test.muz", 0, MIDIFile())
a = tomObj.toMidi("d.muz", 0, MIDIFile(), reapyBol=True, reapyData=take,chanMax=4)
# Пример: запустить воспроизведение
#RPR.OnPlayButton()  # Аналог нажатия Play в Reaper