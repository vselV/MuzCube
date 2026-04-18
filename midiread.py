import mido
from src.MuzCube.UtilClasses.dataClass import Note, NoteOff, Event, Tempo, ProgramChange
from typing import List, Union, Tuple
from dataclasses import dataclass


@dataclass
class MidiDuration:
    seconds: float  # Длина в секундах
    ticks: int  # Длина в тиках
    beats: float  # Длина в долях (quarter notes)
    bars: float  # Длина в тактах (при размере 4/4)


def get_midi_duration(midi_file_path: str) -> MidiDuration:
    """
    Анализирует MIDI-файл и возвращает его длину в разных единицах измерения.

    Args:
        midi_file_path: Путь к MIDI-файлу

    Returns:
        MidiDuration: Объект с длительностью в секундах, тиках, долях и тактах

    Raises:
        ValueError: Если файл не существует или поврежден
    """
    try:
        # Загружаем MIDI-файл
        mid = mido.MidiFile(midi_file_path)

        # Общее время в тиках (максимальное время среди всех треков)
        total_ticks = 0
        for track in mid.tracks:
            track_ticks = sum(msg.time for msg in track)
            total_ticks = max(total_ticks, track_ticks)

        # Конвертируем тики в секунды
        # Создаем временный трек для расчета времени
        temp_track = mido.MidiTrack()
        tempo = 500000  # Стандартный темп (120 BPM)
        time_signature = (4, 4)  # Стандартный размер

        # Ищем установки темпа и размера
        for msg in mid.tracks[0]:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
            elif msg.type == 'time_signature':
                time_signature = (msg.numerator, msg.denominator)

        # Рассчитываем длительность в секундах
        seconds = mid.length

        # Рассчитываем длительность в долях (quarter notes)
        ticks_per_beat = mid.ticks_per_beat
        beats = total_ticks / ticks_per_beat

        # Рассчитываем длительность в тактах (для размера 4/4)
        beats_per_bar = time_signature[0] * (4 / time_signature[1])
        bars = beats / beats_per_bar

        return MidiDuration(
            seconds=seconds,
            ticks=total_ticks,
            beats=beats,
            bars=bars
        )

    except Exception as e:
        raise ValueError(f"Could not process MIDI file '{midi_file_path}': {str(e)}")


def midi_to_events(midi_file_path: str) -> List[Union[Note, NoteOff, Event, Tempo]]:
    """
    Конвертирует MIDI файл в массив событий, объединяя одновременные note_on и pitch_wheel.

    Args:
        midi_file_path: Путь к MIDI файлу

    Returns:
        Список событий (Note, NoteOff, Event, Tempo), отсортированный по времени
    """
    events = []
    active_notes = {}  # Для отслеживания активных нот: {(channel, pitch): note_info}
    pitch_wheel_values = {}  # Текущие значения pitch wheel для каждого канала: {channel: value}

    try:
        mid = mido.MidiFile(midi_file_path)
        ticks_per_beat = mid.ticks_per_beat

        # 1. Собираем все сообщения с их абсолютным временем
        message_times: List[Tuple[int, mido.Message]] = []

        for track in mid.tracks:
            current_time = 0
            for msg in track:
                current_time += msg.time
                message_times.append((current_time, msg))

        # 2. Сортируем сообщения по абсолютному времени
        message_times.sort(key=lambda x: x[0])

        # 3. Обрабатываем сообщения в порядке времени
        for abs_time, msg in message_times:
            # Pitch wheel
            if msg.type == 'pitchwheel':
                channel = msg.channel
                pitch_wheel_values[channel] = msg.pitch

                # Обновляем pitch_wheel для активных нот на этом канале
                for note_key in [k for k in active_notes.keys() if k[0] == channel]:
                    active_notes[note_key]['pitch_wheel'] = msg.pitch
            elif msg.type == 'program_change':
                channel = msg.channel
                change = ProgramChange(
                    start_time=abs_time,
                    channel=channel,
                    program=msg.program
                )
                events.append(change)
            # Note on (velocity > 0)
            elif msg.type == 'note_on' and msg.velocity > 0:
                channel = msg.channel
                pitch = msg.note
                velocity = msg.velocity
                pitch_wheel = pitch_wheel_values.get(channel, 0)

                # Создаем событие Note
                note_event = Note(
                    start_time=abs_time,
                    channel=channel,
                    pitch=pitch,
                    velocity=velocity,
                    pitch_wheel=pitch_wheel,
                    duration = 0
                )
                events.append(note_event)

                # Запоминаем активную ноту
                active_notes[(channel, pitch)] = {
                    'start_time': abs_time,
                    'velocity': velocity,
                    'pitch_wheel': pitch_wheel,
                    'note' : note_event
                }

            # Note off (или note_on с velocity=0)
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                channel = msg.channel
                pitch = msg.note
                note_key = (channel, pitch)

                if note_key in active_notes:
                    note_info = active_notes[note_key]

                    # Создаем NoteOff с сохранением pitch_wheel
                    note_off_event = NoteOff(
                        start_time=abs_time,
                        channel=channel,
                        pitch=pitch,
                        velocity=note_info['velocity'],
                        pitch_wheel=note_info['pitch_wheel']
                    )
                    note_info["note"].duration = abs_time - note_info["note"].start_time
                    events.append(note_off_event)
                    del active_notes[note_key]

            # Control change
            elif msg.type == 'control_change':
                event = Event(
                    start_time=abs_time,
                    channel=msg.channel,
                    num=msg.control,
                    value=msg.value
                )
                events.append(event)

            # Tempo change
            elif msg.type == 'set_tempo':
                tempo = Tempo(
                    start_time=abs_time,
                    bpm=mido.tempo2bpm(msg.tempo),
                    time_num=4,  # Предполагаем размер 4/4
                    time_denum=4
                )
                events.append(tempo)
        # Сортируем события по времени (на всякий случай)
        events.sort(key= lambda x: (
        x.start_time,
        0 if x.__class__.__name__ == 'Tempo' else 1,
        0 if x.__class__.__name__ == 'ProgramChange' else 1
        ))

        return events

    except Exception as e:
        raise RuntimeError(f"Error processing MIDI file: {e}")


# Пример использования
if __name__ == "__main__":
    try:
        duration = get_midi_duration("a.mid")
        print(f"Длительность MIDI-файла:")
        print(f"- Секунды: {duration.seconds:.2f}")
        print(f"- Тики: {duration.ticks} (ticks per beat: {duration.ticks / duration.beats:.0f})")
        print(f"- Доли: {duration.beats:.2f}")
        print(f"- Такты (4/4): {duration.bars:.2f}")
    except ValueError as e:
        print(e)
