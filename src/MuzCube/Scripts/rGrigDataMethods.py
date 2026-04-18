from PyQt6.QtCore import QRectF

from src.MuzCube.UtilClasses.dataClass import *
import math
def calc_speed(tempo,l = 960):
    return 100 / (60 / tempo)
def calc_ppq(x):
    return x / 50 * 240
def calc_pose(x):
    return x / 240 * 50
def calulate(x, y):
    return (x / 50 * 240, - y / 50 * 4096)
def calc_pitch(x, y):
    a = calulate(x, y)
  #  print(x,y)
  #  print(a)
    hi = a[1]
  #  print(hi/4096)
    pitch = int(math.floor(hi / 4096 + 60))
    wheel = int(hi) % 4096
    return (a[0], pitch, wheel)
def correct_pitch(p):
    if p > 0:
        if p < 128:
            return p
        return 127
    return 0
def calc_note(x, y, **kwargs):
    a = calc_pitch(x, y)
    nt = Note(start_time=a[0],
              channel=kwargs.get("channel",0),
              duration=kwargs.get("duration",0),
              pitch=correct_pitch(a[1]),
              pitch_wheel=a[2],
              velocity=kwargs.get("velocity",100),
              )
    return nt
def calc_note_off(x, y, **kwargs):
    a = calc_pitch(x, y)
    nt = NoteOff(start_time=a[0],
              channel=kwargs.get("channel", 0),
              pitch=correct_pitch(a[1]),
              pitch_wheel=a[2],
              velocity=kwargs.get("velocity", 100),
              )
    return nt
def calc_note_rect(rect,**kwargs):
    return calc_note(rect.x(),rect.y(),**kwargs)
def calc_note_off_rect(rect,**kwargs):
    return calc_note_off(rect.x(),rect.y(),**kwargs)
def calc_note_full_rect(rect,**kwargs):
    a = calc_pitch(rect.right(),rect.bottom())
    on = calc_note(rect.left(),rect.bottom(),**kwargs)
    on.duration = a[0]
    nt = NoteOff(start_time=a[0],
                 channel=kwargs.get("channel", 0),
                 pitch=correct_pitch(a[1]),
                 pitch_wheel=a[2],
                 velocity=kwargs.get("velocity", 100),
                 )
    return [on,nt]
def sum_rect(rect):
    return rect.rect().bottomLeft() + rect.pos()
def sum_rect_out(rect):
    dot = sum_rect(rect)
    return QRectF(dot.x(),dot.y()-rect.rect().height(),rect.rect().width(),rect.rect().height())
def sum_off(rect):
    return rect.rect().bottomRight() + rect.pos()
def simple_calc_rect(rect):
    p = sum_rect(rect)
    nt = calc_note_rect(p,velocity = rect.vel, channel = rect.chan)
    b = calc_note_off_rect(sum_off(rect),velocity = rect.vel, channel = rect.chan)
    nt.duration = b.start_time - nt.start_time
    return [nt,b]
def remove_note(notes, note_off):
    for i in range(len(notes)):
        if notes[i].pitch == note_off.pitch:
            notes.pop(i)
            return
def remove_get_chan(notes,note_off):
    for i in range(len(notes)):
        if notes[i].pitch == note_off.pitch and notes[i].pitch_wheel ==  note_off.pitch_wheel:
            note = notes.pop(i)
            return note.channel