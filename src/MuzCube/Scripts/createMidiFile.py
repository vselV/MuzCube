from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from src.MuzCube.UtilClasses import dataClass


def create_midi_from_arrays(arrays, ticks_per_beat=960):
    """
    Создает MIDI файл из массива массивов событий.

    :param arrays: Массив массивов событий (Note, NoteOff, Event, Tempo, ProgramChange, PitchWheel)
    :param ticks_per_beat: Количество тиков на четверть (по умолчанию 960)
    :return: MidiFile объект
    """
    midi = MidiFile(ticks_per_beat=ticks_per_beat)
    track = MidiTrack()
    midi.tracks.append(track)

    # Преобразуем список событий в удобный для обработки формат
    # и сортируем по времени
    all_events = []
    for event_list in arrays:
        all_events.extend(event_list)

    # Сортируем события по времени начала
    all_events.sort(key=lambda x: x.start_time)

    # Обрабатываем события
    current_time = 0
    for event in all_events:
        # Рассчитываем delta_time (разницу во времени с предыдущим событием)
        delta_time = int(event.start_time - current_time)
        current_time = event.start_time

        if isinstance(event, dataClass.Note):
            # Note On сообщение
            track.append(Message('note_on',
                                 channel=event.channel,
                                 note=event.pitch,
                                 velocity=event.velocity,
                                 time=delta_time))
            # Note Off сообщение (через duration тиков)
            note_off_time = int(event.duration)
            track.append(Message('note_off',
                                 channel=event.channel,
                                 note=event.pitch,
                                 velocity=event.velocity,
                                 time=note_off_time))

        elif isinstance(event, dataClass.NoteOff):
            # Отдельное Note Off сообщение
            track.append(Message('note_off',
                                 channel=event.channel,
                                 note=event.pitch,
                                 velocity=event.velocity,
                                 time=delta_time))

        elif isinstance(event, dataClass.Event):
            # Control Change сообщение
            track.append(Message('control_change',
                                 channel=event.channel,
                                 control=event.num,
                                 value=event.value,
                                 time=delta_time))

        elif isinstance(event, dataClass.Tempo):
            # Изменение темпа (используем MetaMessage для set_tempo)
            tempo = bpm2tempo(event.bpm)
            track.append(MetaMessage('set_tempo',
                                     tempo=tempo,
                                     time=delta_time))
            # Также устанавливаем time signature
            track.append(MetaMessage('time_signature',
                                     numerator=event.time_num,
                                     denominator=event.time_denum,
                                     time=0))

        elif isinstance(event, dataClass.ProgramChange):
            # Program Change сообщение
            track.append(Message('program_change',
                                 channel=event.channel,
                                 program=event.program,
                                 time=delta_time))

        elif isinstance(event, dataClass.PitchWheel):
            # Pitch Wheel сообщение
            # Преобразуем значение в диапазон 0-16383 (mido использует 0-16383, а не -8192-8191)
            mido_value = event.value + 8192
            track.append(Message('pitchwheel',
                                 channel=event.channel,
                                 pitch=mido_value,
                                 time=delta_time))

    return midi


def save_midi_to_file(midi, filename='output.mid'):
    """
    Сохраняет MIDI файл на диск.

    :param midi: MidiFile объект
    :param filename: Имя файла для сохранения
    """
    midi.save(filename)
    print(f"MIDI файл сохранен как {filename}")
def createFiles(name,arrays):
    midi = create_midi_from_arrays(arrays)
    save_midi_to_file(midi, name+'.mid')
# Пример использования
if __name__ == "__main__":
    # Создаем тестовые данные
    arrays = [
        # Массив 1
        [
            dataClass.Note(start_time=0, channel=0, pitch=60, velocity=64, pitch_wheel=0, duration=480),
            dataClass.Note(start_time=480, channel=0, pitch=62, velocity=64, pitch_wheel=0, duration=480),
            dataClass.ProgramChange(start_time=0, program=1, channel=0),
            dataClass.Tempo(start_time=0, bpm=120, time_num=4, time_denum=4),
        ],
        # Массив 2
        [
            dataClass.Note(start_time=960, channel=1, pitch=64, velocity=64, pitch_wheel=0, duration=480),
            dataClass.PitchWheel(start_time=960, channel=1, value=4096),
        ]
    ]

    # Создаем MIDI файл
    midi = create_midi_from_arrays(arrays)

    # Сохраняем в файл
    save_midi_to_file(midi, 'example_output.mid')