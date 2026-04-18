import reapy
from reapy import reascript_api as RPR
def serialize(midi_status, pitch_wheel_value,channel):
    code = midi_status | channel
    MSB = (pitch_wheel_value + 8192) >> 7
    LSB = (pitch_wheel_value + 8192) & 0x7F
    return (code,LSB,MSB)
def addReapy(take,note,intPitch,channel,time,currentLen,veloc):
    take.add_note(start=time, end=time+currentLen, pitch=note, channel=channel,velocity=veloc, unit="ppq")
    take.add_event(serialize(0xE0,intPitch,channel), time, unit="ppq")
def addReapy2(take,note,intPitch,channel,time,currentLen,veloc,text):
    addReapy(take,note,intPitch,channel,time,currentLen,veloc)
    text_content = f"NOTE {channel} {note} text {text}"
    text_binary = text_content.encode('utf-8')
   # take.add_sysex(text_binary, time, unit='ppq', evt_type=15)
    text_length = len(text_binary)
    RPR.MIDI_InsertTextSysexEvt(
        take.id,
        False,
        False,  # noSort
        time,  # позиция
        15,  # тип события (15 = REAPER-specific)
        text_content,  # бинарные данные
        text_length,  # длина данных
    )
def addCommand(take,text,time):
    text_content = text
    text_binary = text.encode('utf-8')
    text_length = len(text_binary)
    RPR.MIDI_InsertTextSysexEvt(
        take.id,
        False,
        False,  # noSort
        time,  # позиция
        5,  # тип события (15 = REAPER-specific)
        text_content,  # бинарные данные
        text_length,  # длина данных
    )


def addTempo(bpm, text_sig,position):
    project = reapy.Project()
    numerator = int(text_sig.split[0])
    denominator = int(text_sig.split[1])
    # Добавляем маркер изменения темпа/размера
    RPR.AddTempoTimeSigMarker(
        project.id,  # ID проекта
        -1,  # -1 для новой позиции
        position,  # Позиция в ззй
        -1,  # -1 для нового маркера
        bpm,  # Темп (BPM)
        numerator,  # Числитель
        denominator,  # Знаменатель
        False  # Не переносить айтемы
    )