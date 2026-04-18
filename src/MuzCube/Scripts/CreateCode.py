from src.MuzCube.Scripts import ListParse
from src.MuzCube.Scripts.reapyParse import MusicNote
from src.MuzCube.UtilClasses.FileDict import FileDict

def code_event(event):
    return event.text + "\n"

def code_note(note,base):
    if note.text is not None:
        tex = note.text
    else:
        tex = str(note.pitch - base) + "e"
    return f"add>n{tex}`[{note.start_time},{note.duration}]\n"

def ret_code_ppq(Take,base=60,loads = ""):
    notes = ListParse.ret_notes(Take)
    str_code = ""
    for f in loads:
        str_code += f'load("{f}")'
    for note in notes:
        if type(note) == MusicNote:
            str_code += code_note(note,base)
        else:
            str_code += code_event(note)
    return str_code

def ret_code_only_take(Take,Name,Path):
    dict = FileDict(Path+"/"+Name)
    return ret_code_ppq(Take,base = dict["base"],loads = dict["loads"])
