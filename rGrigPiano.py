import math
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QHBoxLayout, QVBoxLayout, QFrame, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem)
from PyQt6.QtCore import Qt, QRect, QRectF
from PyQt6.QtGui import QPainter, QColor, QBrush, QMouseEvent, QEnterEvent

class KeyRect(QGraphicsRectItem):
    def __init__(self, rect):
        super().__init__(rect)


class VerticalKeyScene(QGraphicsScene):
    octave_pixels = 800
    width_pixels = 300
    black_level = 200

    def __init__(self, parent=None):
        super().__init__(parent)
        self.edo = 22
        self.oct = 2
        self.one_key = self.octave_pixels / self.edo
        self.rectDrawPiano()

    def rectDrawPiano(self):
        data = KeyData(self.edo, self.oct)
        w_b = data.get_black_white_keys()
        white = w_b[0]
        black = w_b[1]
        for ct in range(len(white)):
            item = KeyRect(
                QRectF(0, ct * self.octave_pixels / len(white), self.width_pixels, self.octave_pixels / len(white)))
            self.addItem(item)
        for bl in black:
            item = KeyRect(
                QRectF(0, bl.step * self.one_key, self.width_pixels - bl.level * (self.black_level / bl.max_level),
                       bl.level * self.one_key))
            self.addItem(item)


class KeyInf():
    defoct = 2
    defoct_cent = 1200
    defedo = 12
    def_cent = 100
    minedo = defedo / 16
    mincent = defoct_cent / minedo

    def __init__(self, step, value_cent, edo, oct=2):
        self.step = step
        self.text = ""
        self.edo = edo
        self.value_cent = value_cent
        self.color = 0
        self.level = 0
        self.black = False
        self.vtor_black = False
        self.complete = False
        self.def_width = value_cent / step
        self.width = 0
        self.key_shir = 1

        self.max_level = 1

    def shir_plus(self):
        self.key_shir += 1

    def set_width(self, width):
        self.width = width

    def vtor_black(self):
        self.vtor_black = True
        self.black = True

    def set_text(self, text):
        self.text = text

    def set_color(self, color):
        self.color = color
        self.black = color > 0

    def set_black(self, black):
        self.black = black

    def set_level(self, level):
        self.level = level

    def comp(self):
        self.complete = True

    def is_comp(self):
        return self.complete

    def is_white(self):
        return not self.black


def round_to(step1, edo1, edo2):
    step2 = round(step1 * (edo2 / edo1))
    return step2


class KeyData():
    names7 = {"С": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    names5 = {"C#": 1, "D#": 3, "F#": 6, "G#": 8, "A#": 10}
    ful_dict = {}
    denum = {}
    for i in names7.keys():
        denum[names7[i]] = i
        ful_dict[i] = names7[i]
    for i in names5.keys():
        denum[names5[i]] = i
        ful_dict[i] = names5[i]
    defoct = 2
    defoct_cent = 1200
    defedo = 12
    def_cent = 100
    minedo = defedo / 16
    mincent = defoct_cent / minedo
    alters_up = ["#↑↾𝅄'"]
    alters_down = ["𝄭↓⇂𝅑."]
    list_cents = [70]
    abs_min_delta = 6.6
    x = 50
    for i in range(len(alters_up) - 1):
        x = x / 2
        list_cents.append(x)
    del x

    def __init__(self, edo, oct=defoct):
        self.edo = edo
        self.oct = oct
        self.oct_cf = self.oct / self.defoct
        self.pitch_step = self.defoct_cent / self.edo
        self.min_delta = self.pitch_step / 2
        self.min_delta = min(self.abs_min_delta, self.min_delta)
        self.key_dates = []
        self.keys_dict = {}
        self.fill_keys()

    def to_edo(self, step):
        return round_to(step, self.defedo, self.edo)

    def out_edo(self, step):
        return round_to(step, self.edo, self.defedo)

    def val_cent(self, step):
        return self.pitch_step * self.oct_cf * step

    def get_text(self, step):
        out = self.out_edo(step)
        text = self.denum[out]
        delta = step * self.pitch_step - out * self.def_cent
        ct = 0
        for t in self.list_cents:
            if delta < self.min_delta:
                break
            if math.fabs(delta) < t:
                continue
            if delta < 0:
                delta += t
                text += self.alters_up[ct]
            else:
                delta -= t
                text += self.alters_down[ct]
            ct += 1
        return text

    def first_fill_keys(self):
        for key in self.denum.keys():
            num = self.to_edo(key)
            n_inf = KeyInf(num, self.val_cent(num), self.edo, self.oct)
            n_inf.set_text(self.denum[key])
            if key in self.names5.values():
                n_inf.set_black(True)
            n_inf.comp()
            self.keys_dict[num] = n_inf

    def fill_keys(self):
        if self.edo > self.defedo:
            self.first_fill_keys()
            for i in range(self.edo):
                if self.keys_dict.get(i) is None:
                    self.keys_dict[i] = KeyInf(i, self.val_cent(i), self.edo, self.oct)
                    self.keys_dict[i].vtor_black()
                    self.keys_dict[i].set_text(self.get_text(i))
        elif self.edo <= 7:
            self.full_white()
        else:
            self.fill10edo()
        self.fix_levels()

    def fix_levels(self):
        ct = 0
        max_level = 0
        cur_blacs = []
        for i in range(self.edo):
            if self.keys_dict[i].is_white():
                ct = 0
                cur_blacs = []
                continue
            for k in cur_blacs:
                k.shir_plus()
            ct += 1
            self.keys_dict[i].set_level(ct)
            cur_blacs.append(self.keys_dict[i])
            max_level = max(ct, max_level)
        for i in range(self.edo):
            self.keys_dict[i].max_level = max_level

    def get_black_white_keys(self):
        white = []
        black = []
        for i in range(self.edo):
            if self.keys_dict[i].is_white():
                white.append(self.keys_dict[i])
            else:
                black.append(self.keys_dict[i])
        return white, black

    def full_white(self):
        strin = "CDEFGAB"
        for i in range(self.edo):
            self.keys_dict[i] = KeyInf(i, self.val_cent(i), self.edo, self.oct)
            self.keys_dict[i].set_text(str(strin[i]))
            self.keys_dict[i].comp()

    def fill10edo(self):
        strin = "CDEFGAB"
        for i in range(self.edo):
            self.keys_dict[i] = KeyInf(i, self.val_cent(i), self.edo, self.oct)
            if i % 2 == 1:
                self.keys_dict[i].set_black(True)
                self.keys_dict[i].set_text(str(strin[i // 2]) + "#")
            else:
                self.keys_dict[i].set_text(str(strin[i // 2]))
            self.keys_dict[i].comp()
