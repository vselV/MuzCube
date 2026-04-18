from src.MuzCube.Scripts import byton
from src.MuzCube.UtilClasses.mClass import Message, MusicNote

def from_midi_events(events):
    """
    Создает список нот из набора MIDI-событий

    :param events: список строк с MIDI-событиями
    :return: список объектов MusicNote
    """
    notes = []
    current_notes = {}  # Для отслеживания активных нот (по pitch)
    signature = None
    fulltime = 0
    i = 0
    for event in events:
        parts = event.strip().split()
        if not parts:
            continue

        event_type = parts[0]

        # Обработка события подписи
        if event_type == '<X':
            # Следующая строка содержит base64 данные
            idx = i
            if idx + 2 < len(events) and events[idx + 1].startswith('/') and events[idx + 2] == '>':
                signature_data = events[idx + 1]  # Пропускаем первый символ '/'

                try:
                    signature = byton.decode_midi_text_event(signature_data)
                except:
                    signature = signature_data
                current_notes[pitch]["signature"] = signature
           #      print(signature)
            i+=2
            continue
        if event_type == '<x':
            # Следующая строка содержит base64 данные
            x_parts = events[i].split(" ")
            fulltime += int(x_parts[1])
            idx = i
            if idx + 2 < len(events) and events[idx + 1].startswith('/') and events[idx + 2] == '>':
                signature_data = events[idx + 1]  # Пропускаем первый символ '/'
                try:
                    signature = byton.decode_midi_text_event(signature_data)
                except:
                    signature = signature_data
                notes.append(Message(state = events[i][3:],
                                     start_time = fulltime,
                                     text = signature))
                notes[len(notes)-1].updateType()
            i+=2
            continue
        # Пропускаем закрывающий тег подписи
        if event_type == '>':
            continue

        # Обработка MIDI-событий
        if event_type in ('E', 'e') and len(parts) >= 5:
            time = int(parts[1], 16 if 'x' in parts[1] or 'a' <= parts[1][-1].lower() <= 'f' else 10)
            status = int(parts[2], 16)
            pitch = int(parts[3], 16)
            velocity = int(parts[4], 16)
            fulltime += time
            # Note On событие (velocity > 0)
            if status >> 4 == 0x9 and velocity > 0:
                current_notes[pitch] = {
                    'start_time': fulltime,
                    'velocity': velocity,
                }
                 # Сбрасываем подпись после использования

            # Note Off событие (или Note On с velocity = 0)
            elif (status >> 4 == 0x8) or (status >> 4 == 0x9 and velocity == 0):
                if pitch in current_notes:
                    note_data = current_notes[pitch]
                    duration = fulltime - note_data['start_time']
                   # duration = time - note_data['start_time']
                    notes.append(MusicNote(
                        start_time=note_data['start_time'],
                        duration=duration,
                        pitch=pitch,
                        velocity=note_data['velocity'],
                        signature=note_data.get('signature')
                    ))
                    notes[len(notes)-1].updateTxt()
                    signature = None
                    del current_notes[pitch]
        i+=1

    return notes


def parse_midi_events(text):
    """
    Разбирает текстовое представление MIDI-событий и возвращает список нот

    :param text: строка с MIDI-событиями в указанном формате
    :return: список объектов MusicNote
    """
    # Разбиваем текст на строки и фильтруем пустые
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return from_midi_events(lines)


def sort_objects_by_start_time(objects):
    """
    Сортирует массив объектов по start_time, при совпадении ставит Message перед MusicNote

    :param objects: список объектов с параметром start_time
    :return: отсортированный список
    """
    return sorted(objects, key=lambda x: (
        x.start_time,
        0 if x.__class__.__name__ == 'Message' else 1
    ))
def sorted_ret(data):
    midi_data = data
    if midi_data.startswith('{') and midi_data.endswith('}'):
        midi_data = midi_data[1:-1]

    notes = parse_midi_events(midi_data)
    notes = sort_objects_by_start_time(notes)
    return notes
'''
# Пример использования
midi_data = """{E 0 90 37 60
<X 0 0
/w9OT1RFIDAgNTUgdGV4dCBleGFs
>
<x 480 0 0 0 1 root
/wFyb290
>
E 0 e0 7f 5f
<x 480 0 0 0 5 root
/wVyb290
>
E 0 80 37 00
E 0 90 39 60
<X 0 0
/w9OT1RFIDAgNTcgdGV4dCBoamhraGo=
>
E 960 80 39 00
E 5760 b0 7b 00
CCINTERP 32
CHASE_CC_TAKEOFFS 1}"""

# Удаляем фигурные скобки если они есть
if midi_data.startswith('{') and midi_data.endswith('}'):
    midi_data = midi_data[1:-1]

notes = parse_midi_events(midi_data)
notes = sort_objects_by_start_time(notes)
for note in notes:
    print(note)
'''