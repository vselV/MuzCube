@dataclass
class Note:
    start_time: int  # Время начала в тиках (1 четверть = 960 тиков)
    channel: int  # MIDI канал (0-15)
    pitch: int  # Высота ноты (0-127)
    duration: int  # Длительность в тиках
    pitch_wheel: int  # Значение pitch wheel (-8192 до 8191)


@dataclass
class Event:
    start_time: int  # Время начала в тиках
    channel: int  # MIDI канал (0-15)
    num: int  # Номер события (0-127)
    value: int  # Значение события (0-127)
