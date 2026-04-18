from copy import copy

from src.MuzCube.UtilClasses.FileDict import FileDict
from src.MuzCube.Midi.midi_player import MidiPlaySync
from src.MuzCube.Scripts.rGrigDataMethods import *
from src.MuzCube.Scripts.createMidiFile import *

@dataclass
class DataEvtType:
    poly: bool = False
    text_type: bool  = False
    two_sides : bool = False
    max_value : int = 127
    min_value : int = 0
@dataclass
class DataEvt:
    type: str
    num: int

class EvtVariants:
    dict = FileDict("specialEvt.txt")
    dict_num = {}
    dict_txt_num = {}
    variants  = dict.keys()
    variants_data = []
    def_variants = ["velocity","program","pitch"]
    for variant in variants:
        dict_num[variant]=int(dict[variant])
        dict_txt_num[int(dict[variant])] = variant
        variants_data.append(DataEvt(variant,dict_num[variant]))
    variants_data.sort(key= lambda evt: evt.num)
    all_variants = def_variants
    for variant in variants_data:
        all_variants.append(variant.type)

    bol_dict = {}
    for var in all_variants:
        bol_dict[var] = DataEvtType()
    bol_dict["pan"] = DataEvtType(two_sides = True)
    bol_dict["pitch"] = DataEvtType(two_sides=True, max_value = 8196, min_value = -8196)
    bol_dict["program"] = DataEvtType(text_type = True)
    bol_dict["velocity"] = DataEvtType(poly = True)

class EvtMassiveData:
    def __init__(self):
        self.events_cf = {}
        self.high_pixels = 200

        self.quater_in = 100
        self.quater_out = 960

        self.evt_var = EvtVariants()
        self.pitch_bol = False
    def remove(self,evt):
        self.del_event(self.evt_var.dict_txt_num[evt.num],evt)
    def append(self,evt):
        name = self.evt_var.dict_txt_num[evt.num]
        self.add_event(name,evt)

    def put_events(self,name,events):
        if self.events_cf.get(name):
            self.events_cf[name] += events
        else:
            self.events_cf[name] = events
    def add_event(self,name,evt):
        if self.events_cf.get(name):
            self.events_cf[name].append(evt)
        else:
            self.events_cf[name] = [evt]

    def del_event(self,name,evt):
        if self.events_cf.get(name):
            self.events_cf[name].remove(evt)

    def get_evt(self,name):
        line = self.events_cf.get(name)
        if line is None:
            return []
        bols= self.evt_var.bol_dict[name]
        out_massive = []
        if not bols.poly and not bols.text_type:
            for evt in line:
                out_massive.append((evt[0] / self.quater_in * self.quater_out, evt[1]))
        return out_massive

    def get_playable(self, name):
        out = self.get_evt(name)
        event_massive = []
        num = self.evt_var.dict_num.get(name)
        if num is None:
            num = -1
        for o in out:
            if name == "pitch":
                event_massive.append(PitchWheel(start_time=o[0],channel = o[2].chan, value=o[1]))
            else:
                event_massive.append(Event(start_time=o[0],channel = o[2].channel,num=num,value=o[1]))
        return event_massive

    def get_all_playable(self):
        output = []
        for name in self.events_cf.keys():
            if name != "pitch" or self.pitch_bol:
                output+=self.get_playable(name)
        return output

    def keys(self):
        return self.events_cf.keys()

    def values(self):
        return self.events_cf.values()

    def __setitem__(self, key, value):
        self.events_cf[key] = value

    def __getitem__(self, key):
        return self.events_cf[key]

    def __delitem__(self, key):
        del self.events_cf[key]

    def __contains__(self, key):
        return key in self.events_cf
def remove10(mass,i=9):
    mass.remove(i)
def norm_range(range_val,dot=9):
    out = []
    for i in range_val:
        if i < dot:
            out.append(i)
        else:
            out.append(i+1)
    return out
def all_chan_events(evt,chan_range):
    mass_evt = []
    for i in chan_range:
        nt = copy(evt)
        nt.channel = i
        mass_evt.append(nt)
    return mass_evt
class NoteMassiveData:
    def __init__(self):
        self.note_rects = []
        self.events = EvtMassiveData()
        self.quater_in = 100
        self.quater_out = 960
        self.auto_bol = True
        self.last_auto_chan = 0
        self.range = range(16)
        self.drums = False
        self.all_chan_evt = True
        self.event_bol = True
        self.chanel_range = 1

        self.notes = None
        self.notes_back = False
    def set_range(self,range):
        self.range = range
    def set_range_str(self,range_str):
        splited =  range_str.split(",")
        nums = []
        for s in splited:
            if "-" in s:
                spl2 = s.split("-")
                nums += range(int(spl2[0]),int(spl2[1]) + 1)
            else:
                nums.append(int(s))
        self.range = nums
    def get_auto_playable_notes(self,chan_range):
        notes = self.get_playable_notes()
      #  self.chanel_adapt(notes,chan_range)
        return sorted(notes,key = lambda ev : ev.start_time)
    def drum_notes(self, notes):
        for note in notes:
            note.channel = 9
    def get_drum(self):
        notes = self.get_playable_notes()
        self.drum_notes(notes)
        return notes
    def all_include_playable(self):
        if self.notes_back:
            notes = self.notes
            self.notes_back = False
        else:
            if self.drums:
                notes = self.get_drum()
            else:
                notes = self.get_auto_playable_notes(self.range)
        print(notes)
        out = notes
        if self.event_bol and (self.events is not None):
            events = self.events.get_all_playable()
            if self.drums:
                for evt in events:
                    if isinstance(evt,PitchWheel):
                        events.remove(evt)
                    else:
                        evt.channel = 9
                out += events
            elif self.all_chan_evt:
                for evt in events:
                    out += all_chan_events(evt,self.range)
            else:
                out += events
        print(out)
        return sorted(out,key = lambda e: e.start_time)
    def chanel_adapt(self):
        if self.notes is not None:
            notes = self.notes
        else:
            notes = self.get_playable_notes()
        self.last_auto_chan = 0
        mass = []
        ct = 0
        for note in notes:
            if isinstance(note, Note):
                note.channel = self.range[(ct%len(self.range))]
                ct += 1
                self.last_auto_chan = max(ct,self.last_auto_chan)
                mass.append(note)
            elif isinstance(note, NoteOff):
                ct -= 1
                note.channel = remove_get_chan(mass,note)
        return self.last_auto_chan <= len(self.range)

    def set_events(self, events):
        self.events = events

    def get_playable_notes(self):
        out = []
        for rect in self.note_rects:
            out += simple_calc_rect(rect)
        return out

    def get_playable(self):
        out = self.get_playable_notes()
        if self.events is not None:
            out += self.events.get_all_playable()
        return out

    def append_rect(self,rect):
        self.note_rects.append(rect)
        print(self.note_rects)
    def append_evt(self,evt):
        if self.events is not None:
            self.events.append(evt)
    def remove_rect(self,rect):
        self.note_rects.remove(rect)
        print(self.note_rects)
    def remove_evt(self, evt):
        if self.events is not None:
            self.events.remove(evt)
    def back_notes(self):
        if not self.notes_back:
            if self.drums:
                self.notes = self.get_drum()
            else:
                self.notes = self.get_auto_playable_notes(self.range)
            self.notes_back = True
    def calc_auto_channel_range_before_render(self):
        self.back_notes()
        self.last_auto_chan = 0
        ct = 0
        for note in self.notes:
            if isinstance(note, Note):
                ct += 1
                self.last_auto_chan = max(ct, self.last_auto_chan)
            elif isinstance(note, NoteOff):
                ct -= 1
        self.chanel_range = self.last_auto_chan
        return self.last_auto_chan
    def get_auto_play_all(self):
        self.calc_auto_channel_range_before_render()
        return self.all_include_playable()
   # def get_one_massive_data(self):

    def __getitem__(self, key):
        return self.note_rects[key]
    def __setitem__(self, key, value):
        self.note_rects[key] = value
    def __delitem__(self, key):
        del self.note_rects[key]
    def __contains__(self, key):
        return key in self.note_rects

class AllNotesEvtData:
    def __init__(self, midi_player : MidiPlaySync, tracks = None):
        self.for_all_midi_player = midi_player

        self.tracks = {}
        self.track_ids = {}
        self.name_to_id = {}
        self.count_tracks = 0

        self.visible_interactions = False
        self.one_solo = False
        self.last_full_render_boolean = False

        self.current_track = None
        if tracks is not None:
            for key in tracks.keys():
                self.set_track(key, tracks[key])
        else:
            self.add_new_track("track")

    def open_files(self):
        s = 0

    def save_as(self, filename):
        createFiles(filename,self.full_auto_range_render())
        #сетка
    def _up_one_solo(self):
        self.one_solo = False
        for track in self.tracks.values():
            if track.solo:
                self.one_solo = True
                return
    def _visibilities(self):
        for track in self.tracks.values():
            if track is not self.current_track:
                track.off()
                if track.visible_midi:
                    track.all_vis()
                else:
                    track.all_invis()
            else:
                track.on()
    def get(self,key):
        if type(key) == str:
            return self.tracks.get(key)
        else:
            return self.track_ids.get(key)
    def set(self,key,value):
        if type(key) == str:
            self.set_track(key,value)
        else:
            print("бля")
    def rename_track(self,name: str,new_name:str):
        if not self.tracks.get(new_name):
            self.tracks[new_name] = self.tracks.pop(name)
            self.name_to_id[new_name] = self.name_to_id.pop(name)
        else:
            print("ёпт")
    def append_rect(self,rect):
        if self.current_track:
            self.current_track.append_rect(rect)
    def append_evt(self,evt):
        if self.current_track:
            self.current_track.append_evt(evt)
    def remove_rect(self,rect):
        if self.current_track:
            self.current_track.remove_rect(rect)
    def remove_evt(self,evt):
        if self.current_track:
            self.current_track.remove_evt(evt)
    def set_track(self, name, track):
        if not self.tracks.get(name) and track is not None:
            self.track_ids[self.count_tracks] = track
            self.name_to_id[name] = self.count_tracks
            self.count_tracks += 1
            self._cur(track)
        self.tracks[name] = track
        track.set_midi_player(self.for_all_midi_player)

    def add_new_track(self, name):
        self.tracks[name] = MidiTrack(self.for_all_midi_player,oto = self)
        self.track_ids[self.count_tracks] = self.tracks[name]
        self.name_to_id[name] = self.count_tracks
        self.count_tracks += 1
        self._cur(self.tracks[name])

    def remove_track(self, name ):
        del self.tracks[name]
        del self.track_ids[self.name_to_id.get(name)]
        del self.name_to_id[name]

    def play_all(self,start_time):
        for track in self.tracks.values():
            if track.is_playing():
                track.play(start_time)
    def set_current(self,name):
        self.current_track.all_dark()
        self.current_track = self.tracks.get(name)
        self.current_track.all_norm()
    def _cur(self,track):
        if self.current_track is None:
            self.current_track = track
    def track(self):
        return self.tracks.get(self.current_track)
    def auto_range_ports(self):
        dict = {}

        for track in self.tracks.values():
            if dict.get(track.port_name) is None:
                dict[track.port_name] = [track]
            else:
                dict[track.port_name].append(track)
        print(dict)
        for val in dict.keys():
            ct = 0
            drums = 0
            for tr in dict[val]:
                if not tr.drums:
                    ct+=tr.chanel_range
                else:
                    drums+=1
            if drums <= 1 and ct <= 15:
                ct = 0
                for tr in dict[val]:
                    if not tr.drums:
                        print("------------------",norm_range(range(ct,ct + tr.chanel_range)))
                        tr.set_range(norm_range(range(ct,ct + tr.chanel_range)))
                        ct += tr.chanel_range
            else:
                return False
        return True
    def full_auto_range_render(self):
        print(self.tracks)
        for track in self.tracks.values():
            track.calc_auto_channel_range_before_render()
        self.last_full_render_boolean = self.auto_range_ports()
        out = []
        for track in self.tracks.values():
           # print((track.port_name,track.all_include_playable()))
            track.chanel_adapt()
            out.append((track.port_name,track.all_include_playable()))
        return out
    def full_one_massive_render(self):
        massive = self.full_auto_range_render()
        out = []
        for m in massive:
            for item in m[1]:
                item.port_name = m[0]
                out.append(item)
        return out
    def play_auto_full_all(self,start_time,loop_times=None):
        render = self.full_auto_range_render()
        self.for_all_midi_player.play_all(render,start_time,loop_times)
    def stop_auto_full_all(self):
        self.for_all_midi_player.stop_all()
    def __getitem__(self, key):
        return self.get(key)
    def __setitem__(self, key, value):
        self.set(key,value)
    def __delitem__(self, key):
        self.remove_track(key)
    def __contains__(self, key):
        return key in self.tracks or key in self.track_ids

class MidiTrack(NoteMassiveData):
    def __init__(self,midi_player : MidiPlaySync ,port = "loopMIDI Port 1 5", oto : AllNotesEvtData = None):
        super().__init__()
        #print("port")
        self.oto = oto
        self.muted = False
        self.solo = False
        self.visible_midi = True
        self.visible_track = True
        self.port_name = port
        self.midi_player = midi_player
        self.init_port()
        self.player = self.midi_player.players.get(self.port_name)
        self.pob_bol = True

    def init_port(self):
        self.port_name = self.midi_player.open_player(self.port_name)
    def set_midi_player(self,player):
        self.midi_player = player
        self.init_port()
    def set_oto(self,oto):
        self.oto = oto
    def one_sol(self):
        if self.oto is not None:
            self.oto._up_one_solo()
    def mute(self):
        self.muted = not self.muted
     #   self._update_mute()
    def solo(self):
        self.solo = not self.solo
        self.one_sol()
      #  self._update_mute()
    def get_one_sol(self):
        if self.oto is not None:
            return self.oto.one_solo
        return False
    def _update_mute(self):
        if self.is_playing():
            self.off()
        else:
            self.on()
    def off(self):
        for note in self.note_rects:
            note.mute()
    def on(self):
        for note in self.note_rects:
            note.unmute()
    def all_vis(self):
        self.visible_midi = True
        for note in self.note_rects:
            note.setVisible(True)
    def all_invis(self):
        self.visible_midi = False
        for note in self.note_rects:
            note.setVisible(False)
    def all_dark(self):
        self.pob_bol = True
        for note in self.note_rects:
            note.dark()
    def all_norm(self):
        self.pob_bol = False
        for note in self.note_rects:
            note.normal()
    def pob_vis(self):
        self.off()
        self.all_vis()
        self.all_dark()
    def root_vis(self):
        self.on()
        self.all_vis()
        self.all_norm()
    def is_playing(self):
        return (self.muted or self.get_one_sol()) and not self.solo

    def play(self,start_time):
        what_play = self.get_auto_play_all()
        self.midi_player.play_all([(self.midi_player,what_play)],start_time)
    def stop(self):
        self.midi_player.stop_all()


print(EvtVariants().all_variants)
