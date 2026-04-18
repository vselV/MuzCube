from dataclasses import dataclass
import copy
from src.MuzCube.UtilClasses.dataClass import Note, NoteOff


@dataclass
class InterData:
    rootm: str  # Время изменения темпа в тиках
    octave: int  # Новый темп (ударов в минуту)
    conceptOct: float

class Message:
    def __init__(self,state, start_time, type = None, text = None):
        self.parent_inter = None
        self.parent = None

        self.state = state
        self.start_time = start_time
        self.type = type
        self.text = text
    def __repr__(self):
        return f"Message(start={self.start_time}, type={self.type}, text={self.text})"
    def updateType(self):
        if self.state is not None:
            self.type = int(self.state.split(" ")[4])

    def set_parent_inter(self,inter):
        self.parent_inter = inter

    def render(self):
        self.parent_inter.evalContex(self.text)

    def reposition(self, **kwargs):
        self.start_time = kwargs.get("start_time", self.start_time)
        self.parent.changes = True

    def retext(self,text):
        self.text = text
        self.parent.changes = True

class MusicNote:
    def __init__(self, start_time, duration, pitch, velocity, signature=None):
        self.parent_inter = None
        self.inter_data = None

        self.parent = None
        self.base = 60

        self.start_time = start_time
        self.duration = duration
        self.pitch = pitch
        self.velocity = velocity
        self.signature = signature

        self.pitch_wheel = 0
        self.channel = 0

        self.chord_wheel = 0

        self.text_type = None
        self.text = None

        self.note_on = None
        self.note_off = None

    def __repr__(self):
        return f"MusicNote(start={self.start_time}, duration={self.duration}, pitch={self.pitch}, velocity={self.velocity}, text={self.text})"

    def set_parent_inter(self,inter):
        self.parent_inter = inter

    def updateTxt(self):
        if self.signature != None:
            self.text = self.signature.split(" ")[4]
            self.text_type = self.signature.split(" ")[3]

    def render(self,**kwargs):
        if not kwargs.get("ch_bol", False):
            self.inter_data = self.parent_inter.get_inter_data()
        nRoot = self.parent_inter.sum_pitch(self.inter_data.rootm,"0",self.text,self.inter_data.conceptOct,self.inter_data.octave)
        self.pitch = self.base + nRoot[0]
        self.pitch_wheel = self.parent_inter.toPitch(nRoot[1])
        self.chord_wheel = self.pitch * 8192 + self.pitch_wheel
        self.note_on = Note(self.start_time, self.channel, self.pitch, self.velocity,self.pitch_wheel,self.duration)
        self.note_off = NoteOff(self.start_time + self.duration, self.channel, self.pitch, self.velocity, self.pitch_wheel)

    def reposition(self, **kwargs):
        self.start_time = kwargs.get("start_time", self.start_time)
        self.duration = kwargs.get("duration", self.duration)
        self.note_on.start_time = self.start_time
        self.note_off.start_time = self.start_time + self.duration

        self.parent.changes = True
    def retext(self,text):
        self.text = text
        self.render(ch_bol=True)

    def re_on_off(self):
        self.note_on = Note(self.start_time, self.channel, self.pitch, self.velocity, self.pitch_wheel,self.duration)
        self.note_on = NoteOff(self.start_time + self.duration, self.channel, self.pitch, self.velocity, self.pitch_wheel)

class MidiMassive:
    def __init__(self,defCon,**kwargs):
        self.inter_init = kwargs.get("inter_init")

        self.music_all = kwargs.get("sort_all",[])
        self.changes = False

        self.music_notes = []
        self.messages = []

        for n in self.music_all:
            n.set_parent_inter(self.inter_init)
            if type(n) is MusicNote:
                self.music_notes.append(n)
            elif type(n) is Message:
                self.messages.append(n)
        self.message_bol = len(self.messages) != 0

        self.events = kwargs.get("events", [])
        self.tempo_change = kwargs.get("tempo_change", [])


        self.inter_evt = kwargs.get("interEvt", [])
        self.evt_play = []
    def re_init_inter(self):
        if self.inter_init != None:
            self.inter_init.re_init(self.inter_init.kwargs)
    def render_notes(self):
        self.music_all.sort(key=lambda x: x.start_time)
        for n in self.music_all:
            n.render()
        self.re_init_inter()
    def first_fill_play(self):
        for tmp in self.tempo_change:
            self.evt_play.append(tmp)
        for event in self.events:
            self.evt_play.append(event)
        for note in self.music_notes:
            self.evt_play.append(note.note_on)
            self.evt_play.append(note.note_off)
    def get_play_sorted(self):
        if self.changes:
            self.render_notes()
        self.evt_play = sorted(self.evt_play, key= lambda x: (
        x.start_time,
        0 if x.__class__.__name__ == 'Tempo' else 1
        ))
        return self.evt_play
    def delete_note(self,note):
        self.music_notes.remove(note)
        self.music_all.remove(note)
        self.evt_play.remove(note.note_on)
        self.evt_play.remove(note.note_off)
    def add_note(self,note):
        self.music_notes.append(note)
        if self.message_bol:
            note.re_on_off()
        else:
            note.render(ch_bol = True)
        self.evt_play.append(note.note_on)
        self.evt_play.append(note.note_off)
        self.changes = True
    def add_message(self,message):
        self.messages.append(message)
        self.music_all.append(message)
        self.message_bol = len(self.messages) != 0
        self.changes = True
    def delete_message(self, message):
        self.messages.remove(message)
        self.music_all.remove(message)
        self.message_bol = len(self.messages) != 0
        self.changes = True
    def add_tempo(self,tempo):
        self.tempo_change.append(tempo)
        self.evt_play.append(tempo)
    def delete_tempo(self,tempo):
        self.tempo_change.remove(tempo)
        self.evt_play.remove(tempo)
    def add_event(self,event):
        self.tempo_change.append(event)
        self.tempo_change.append(event)
    def delete_event(self, event):
        self.tempo_change.remove(event)
        self.tempo_change.remove(event)
    def get_start(self,position):
        mass_notes = []
        for n in self.music_notes:
            if n.start_time < position:
                if n.start_time + n.duration > position:
                    note = copy.copy(n.note_on)
                    note.start_time = position
                    mass_notes.append(note)
        return mass_notes
