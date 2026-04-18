from dataclasses import dataclass

@dataclass
class Note:
    start_time: float  # Время начала в тиках (1 четверть = 960 тиков)
    channel: int  # MIDI канал (0-15)
    pitch: int  # Высота ноты (0-127)
    velocity: int  # Громкость ноты (1-127)
    pitch_wheel: int  # Значение pitch wheel (-8192 до 8191)
    duration: float
    #metadata
    port_name: str = ""
    label:str = ""
    coord: tuple = (0, 0, 0)

@dataclass
class NoteOff:
    start_time: float  # Время начала в тиках (1 четверть = 960 тиков)
    channel: int  # MIDI канал (0-15)
    pitch: int  # Высота ноты (0-127)
    velocity: int  # Громкость ноты (1-127)
    pitch_wheel: int  # Значение pitch wheel (-8192 до 8191)
    #metadata
    port_name : str  = ""
    label: str = ""
    coord: tuple = (0, 0, 0)


@dataclass
class Event:
    start_time: float  # Время начала в тиках
    channel: int  # MIDI канал (0-15)
    num: int  # Номер события (0-127)
    value: int  # Значение события (0-127)
    # metadata
    port_name: str = ""

@dataclass
class Tempo:
    start_time: float  # Время изменения темпа в тиках
    bpm: float  # Новый темп (ударов в минуту)
    time_num: int
    time_denum: int


@dataclass
class ProgramChange:
    start_time: float  # Время изменения темпа в тиках
    program: int
    channel: int
    # metadata
    port_name: str = ""

@dataclass
class PitchWheel:
    start_time: float  # Время изменения темпа в тиках
    channel: int
    value: int
    # metadata
    port_name: str = ""


class PortEvent():
    def __init__(self, port,event):
        self.port_name = port
        self.event = event


def par_note(note_on,note_off):
    bol = True
    bol = bol and (note_on.channel == note_off.channel)
    bol = bol and (note_on.pitch == note_off.pitch)
    bol = bol and (note_on.velocity == note_off.velocity)
    bol = bol and (note_on.pitch_wheel == note_off.pitch_wheel)
    return bol