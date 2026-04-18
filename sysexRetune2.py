import time

import mido
import math
import struct


def frequencyTransform(freq):
    """Точная копия из MIDIUtil"""
    resolution = 16384
    freq = float(freq)
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


def sendMIDITuningStandard(outport, tunings, sysExChannel=0x7F, realTime=True, tuningProgram=0):
    """
    Прямой порт метода changeNoteTuning из MIDIUtil для отправки через mido
    """
    # Создаем payload как в оригинальном методе
    payload = struct.pack('>B', tuningProgram)
    payload += struct.pack('>B', len(tunings))

    for (noteNumber, frequency) in tunings:
        payload += struct.pack('>B', noteNumber)
        MIDIFrequency = frequencyTransform(frequency)
        for byte in MIDIFrequency:
            payload += struct.pack('>B', byte)

    # Создаем Universal SysEx сообщение
    sysex_data = []

    if realTime:
        sysex_data.append(0x7F)  # Real-time
    else:
        sysex_data.append(0x7E)  # Non-real-time

    sysex_data.append(sysExChannel)  # SysEx channel
    sysex_data.append(0x08)  # Code: MIDI Tuning Standard
    sysex_data.append(0x02)  # Subcode: Single Note Tuning Change

    # Добавляем payload
    for byte in payload:
        sysex_data.append(byte)

    # Создаем и отправляем сообщение
    sysex_message = mido.Message('sysex', data=sysex_data)
    outport.send(sysex_message)

    print(f"Отправлен tuning change для {len(tunings)} нот")


# Пример использования
if __name__ == "__main__":
    try:
        outport = mido.open_output("loopMIDI Port 1")
        outport.send(mido.Message(
            'note_on',
            channel=0,
            note=60,
            velocity=100
        ))
        time.sleep(2)

        # Создаем список тюнингов как в оригинальном примере MIDIUtil
        # Нота 60 (C5) с частотой, соответствующей +20 центам
        base_freq = 440.0
        target_freq = base_freq * math.pow(2, (60 - 69 + 20 / 100.0) / 12.0)
        tunings = [(60, target_freq)]

        # Отправляем тюнинг
        sendMIDITuningStandard(outport, tunings)
        outport.send(mido.Message(
            'note_on',
            channel=0,
            note=60,
            velocity=100
        ))
        time.sleep(2)
        outport.close()

    except Exception as e:
        print(f"Ошибка: {e}")