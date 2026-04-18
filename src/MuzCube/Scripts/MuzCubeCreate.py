from Scripts.reapyParse import MusicNote, Message
from src.MuzCube.Scripts.reapyParse import *
def toBeats(tiks):
    return tiks/960
def fromMass(mass,base):
    strout = ""
    for note in mass:
        if type(note) is MusicNote:
            if note.text is not None:
                note_text = note.text
            else:
                note_text = f"{note.pitch-base}e"
            strout+=f"APIadd({note.start_time},{note.duration},{note.velocity},{note_text})\n"
        elif type(note) is Message:
            strout += note.text + "\n"
    return strout