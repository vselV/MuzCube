import mido
import time
import math

outport = mido.open_output("loopMIDI Port 1")
def frequency_transform(freq):
    """
    Точная копия функции frequencyTransform из MIDIUtil
    Возвращает три байта для представления частоты в MIDI Tuning Standard
    """
    resolution = 16384
    dollars = 69 + 12 * math.log(freq / 440.0, 2)
    firstByte = int(dollars)
    lowerFreq = 440 * math.pow(2.0, ((float(firstByte) - 69.0) / 12.0))
    centDif = 1200 * math.log((freq / lowerFreq), 2) if freq != lowerFreq else 0
    cents = round(centDif / 100 * resolution)
    secondByte = min(cents >> 7, 0x7F)
    thirdByte = min(cents - (secondByte << 7), 0x7F)

    if thirdByte == 0x7F and secondByte == 0x7F and firstByte == 0x7F:
        thirdByte = 0x7E

    return [firstByte, secondByte, thirdByte]


def send_note_tuning_change(note_number, cents_offset, channel=0):
    """
    Отправляет изменение тюнинга для одной ноты через SysEx
    """
    try:


        # Рассчитываем целевую частоту
        semitones = cents_offset / 100.0
        target_freq = 440.0 * math.pow(2, (note_number - 69 + semitones) / 12.0)

        # Получаем байты тюнинга
        tuning_bytes = frequency_transform(target_freq)

        # Создаем Universal SysEx сообщение
        # Формат: F0 7F 7F 08 02 note msb lsb F7
        sysex_data = [
            0x7F,  # Universal Real-Time
            0x7F,  # Device ID (7F = все устройства)
            0x08,  # Sub-ID: MIDI Tuning Standard
            0x02,  # Sub-ID2: Single Note Tuning Change
            note_number,  # Номер ноты
            tuning_bytes[1],  # MSB центов
            tuning_bytes[2]  # LSB центов
        ]

        sysex_message = mido.Message('sysex', data=sysex_data)
        outport.send(sysex_message)

        print(f"Microtuning sent: Note {note_number}, {cents_offset:+} cents")
        print(f"Target frequency: {target_freq:.2f} Hz")

        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

# Пример использования: повысить ноту 60 на 20 центов

   # print(f"Нота {note_number}: {cents:+} центов")
print(mido.get_output_names())

# Пример использования
outport.send(mido.Message(
            'note_on',
            channel=0,
            note=60,
            velocity=100
        ))
time.sleep(2)
send_note_tuning_change(60, 50)  # Повысить ноту 60 на 20 центов
outport.send(mido.Message(
            'note_on',
            channel=0,
            note=60,
            velocity=100
        ))
time.sleep(2)
#send_single_note_tuning(64, -15)  # Понизить ноту 64 на 15 центов