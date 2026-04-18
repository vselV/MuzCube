
from typing import List

#from PyQt6.QtNetwork.QUdpSocket import kwargs

from sympy import Rational
from PyQt6.QtWidgets import  QGraphicsScene
from PyQt6.QtGui import QPen, QColor, QFont, QBrush

from src.MuzCube.Dialogs.eGrigDialog import show_search_dialog

from src.MuzCube.Lex.tomObj import toMidi
import math
from src.MuzCube.UtilClasses.QtKeyTest import clear
from src.MuzCube.Wigets.rGrigHeadItems import HeadRect

from src.MuzCube.UtilClasses.rGrigPyKeys import (KeyData, KeyInf, KeyColorsObj)
from dataclasses import dataclass
import pickle

def primfacs(n):
   i = 2
   primfac = []
   while i * i <= n:
       while n % i == 0:
           primfac.append(i)
           n = n / i
       i = i + 1
   if n > 1:
       primfac.append(n)
   return primfac

def new_value(x,step,max_x,min_x):
    xo = x + step
    if xo > max_x:
        return max_x
    if xo < min_x:
        return min_x
    return xo

def make_color_dimmer(color, factor=0.7):
    h, s, v, a = color.hue(), color.saturation(), color.value(), color.alpha()
    new_s = max(0, min(255, int(s * factor)))
    new_v = max(0, min(255, int(v * factor)))
    dimmed_color = QColor.fromHsv(h, new_s, new_v, a)
    return dimmed_color

def pen_brush_dict(dict):
    for key in dict.keys():
        if "pen" in key:
            dict[key] = QPen(dict[key])
            dict[key].setCosmetic(True)
        elif "brush" in key:
            ## print(key)
            dict[key] = QBrush(dict[key])

    return dict

def get_default_rect_dict():
    dict = {}
    dict["normal_brush"] =  QColor(100, 150, 255, 150)
    dict["selected_brush"] = QColor(255, 150, 50, 200)
    dict["mute_brush"] =make_color_dimmer(dict["normal_brush"])

    dict["normal_pen"] =  QPen(QColor(13, 10, 29),1.7)
    dict["mute_pen"] = QColor(13, 10, 29,100)
    return pen_brush_dict(dict)

def get_default_dict():
    dict = {}
    dict['background'] = QColor(255, 255, 255)
    dict['background_head'] = QColor(122, 122, 122)

    dict['root_line_pen'] = QColor(230, 217, 69)
    dict['block_pen'] = QPen(QColor(144, 235, 41),1.3)
    dict['x_text_pen'] = QColor(126, 193, 114)

    dict['grid_pen'] = QColor(170, 170, 170)
    dict['text_pen'] = QColor(100, 100, 100)
    dict['h_line_pen'] = QColor(250, 250, 250)

    dict['evt_pen'] = QPen(QColor(50, 120, 150),1.5)
    dict['evt_x_pen'] = QPen(QColor(94, 185, 193),1.5)
    dict['evt_y_pen'] = QPen(QColor(193, 122, 81),1.5)

    dict['head_brush'] = QColor(200, 220, 210, 200)
    dict['loop_brush'] = QColor(250, 250, 250, 100)
    dict['head_pen'] = QColor(230, 230, 230, 200)
    dict['loop_pen'] = QColor(250, 250, 250, 100)
    dict['solid_loop_brush'] = dict['loop_pen']
    return pen_brush_dict(dict)

class ColorRect():
    def __init__(self,dict):
        self.normal_brush = dict['normal_brush']
        self.selected_brush = dict['selected_brush']
        self.mute_brush = dict['mute_brush']

        self.normal_pen = dict['normal_pen']
        self.mute_pen = dict['mute_pen']
class DefaultColorRect(ColorRect):
    def __init__(self):
        super().__init__(get_default_rect_dict())

class ColorGrid():
    def __init__(self,dict):
        self.dict = dict
        self.background = dict['background']
        self.background_head = dict['background_head']

        self.root_line_pen = dict.get('root_line_pen')
        self.block_pen = dict.get('block_pen')
        self.grid_pen = dict.get('grid_pen')

        self.text_pen = dict.get('text_pen')
        self.x_text_pen = dict.get('x_text_pen')

        self.evt_pen = dict.get('evt_pen')
        self.evt_x_pen = dict.get('evt_x_pen')
        self.evt_y_pen = dict.get('evt_y_pen')
        self.h_line_pen = dict.get('h_line_pen')

        self.pens = None
        self.pens_count = 5
        self.alpha_step = 80
        self.fill_pens()

        self.head_brush = dict.get('head_brush')
        self.head_pen = dict.get('head_pen')
        self.loop_brush = dict.get('loop_brush')
        self.loop_pen = dict.get('loop_pen')

    def fill_pens(self):
        self.pens = []
        ct = 0
        while self.dict.get('pen' + str(ct)):
            self.pens.append(self.dict['pen' + str(ct)])
            ct += 1
        if ct == 0:
            for i in range(self.pens_count):
                self.pens.append(self._get_pen(i))
        else:
            self.pens_count = ct
    def get_pen(self,level):
        if level < self.pens_count:
            return self.pens[level]
        return self.pens[-1]
    def _get_pen(self,level):
        if level == 0:
            return self.grid_pen
        color = self.grid_pen.color()
        alpha = color.alpha()
        out_pen = QPen(QColor(color.red(),color.green(),color.blue(),new_value(alpha, - self.alpha_step * level,255,0)))
        out_pen.setCosmetic(True)
        ## print(out_pen.color().alpha())
        return out_pen
class DefaultColorGrid(ColorGrid):
    def __init__(self):
        super().__init__(get_default_dict())
class Scale():
    pitch_wheel_const = 4096
    def __init__(self, interpr : toMidi, name : str, str=None, **kwargs):
        self.interpr = interpr
        self.name = name
        if str is not None:
            args = eval(f"({str})")
            self.interpr.scale(*args)
        self.notes_str = self.interpr.TempDict.get(name)
        self.kwargs_str = self.interpr.tempKwargs.get(name)

        self.notes_rev = list(reversed(self.notes_str))

        self.pitches = []
        self.chord_y = []
        self.root = 0
        self.to_rect = 50
        self.to_pitch = 0.5
        self.fuloctave = 600
        self.edo = self.kwargs_str.get('edo',12)
        self.conceptOct = self.kwargs_str.get('oct',2)
        self.simp_num = self.kwargs_str.get("simp_num", self.interpr.simpleNumbers)
        self.set_to_rect(50)
        self.calc_pitches()
        self.chord_calc_only_pitch()

    def calc_pitches(self):
        for n in range(len(self.notes_str)):
            ## print(self.name,n)
            self.pitches.append(self.interpr.fromTmp(n,self.name))
        start_pitch = self.pitches[0]
        for i in range(len(self.pitches)):
            self.pitches[i] = self.pitches[i] - start_pitch

    def get_all_key_inf(self):
        key_mass = []
        for i in range(len(self.chord_y)):
            if i == len(self.chord_y)-1:
                len_key = self.fuloctave - self.chord_y[-1]
            else:
                len_key = self.chord_y[i+1] - self.chord_y[i]
            shir_key = len_key // 1200
            key = KeyInf(i,self.chord_y[i],cent_shir = shir_key)
            key.set_scaled(True)
            key_mass.append(key)
        return key_mass

    def snap_y(self,y,base,return_tup=False):
        base_n = base
        base_n2 = base
        pt = 0
        ct = 0
        oct = 0
        oct_2 = 0
        menz = True
        if base < y:
            while base_n + oct < y:
                base_n2 = base_n
                oct_2 = oct
                base_n = base + self.chord_y[pt]
                ct += 1
                pt = ct % len(self.chord_y)
                if pt == 0:
                    oct += self.fuloctave
        elif base > y:
            menz = False
            ct = -1
            pt = -1
            while base_n + oct > y:
                oct_2 = oct
                if pt == len(self.chord_y) - 1:
                    oct -= self.fuloctave
                ct -= 1
                pt = ct % len(self.chord_y)
                base_n2 = base_n
                base_n = base + self.chord_y[pt]
        else:
            return self.return_tup(base,pt,return_tup)
        if menz:
            pt = (pt-1) % len(self.chord_y)
        if math.fabs(oct+base_n-y) < math.fabs(oct_2+base_n2-y):
            return self.return_tup(oct+base_n,pt,return_tup)
        return self.return_tup(oct_2+base_n2,pt,return_tup)
    def return_tup(self,base,i,ret_tup=False):
        ## print(ret_tup)
        if ret_tup:
            return (base,i)
        return base
    def convert_pitch(self,pitch):
        y = pitch/self.to_pitch
        return y
    def set_to_rect(self,semitone):
        self.to_rect = semitone / self.pitch_wheel_const
        self.fuloctave = self.to_rect * (self.pitch_wheel_const * math.log(self.conceptOct,math.pow(2,1/12)))
    def chord_calc_only_pitch(self):
        self.chord_y = []
        for n in self.pitches:
            self.chord_y.append(self.fuloctave-self.to_pitch * n)
        self.chord_y[0] = self.chord_y[0] - self.fuloctave
        self.chord_y = list(reversed(self.chord_y))
    def chord_calc(self):
        self.chord_y = []
        for n in self.pitches:
            self.chord_y.append(self.to_rect * (n[0]*self.pitch_wheel_const+n[1]))
    def get_abs(self,num):
        n = num // len(self.chord_y)
        m = num %  len(self.chord_y)
        ans = n * self.fuloctave
        uset  = self.chord_y[m]
        if m < 0:
            uset = uset - self.fuloctave
        return int(ans+uset)
    def base_to_screen(self,start,end,base):
        n_base = base
        if base > start and base < end:
            return n_base
        elif base < start:
            while n_base < start:
                n_base += self.fuloctave
            return n_base
        else:
            while n_base > end:
                n_base -= self.fuloctave
            return n_base
    def get_coord(self,i):
        return self.chord_y[i%(len(self.chord_y))]
    def get_grid(self,start,end,base):
        base_on_screen = self.base_to_screen(start,end,base)
        base_n = base_on_screen
        grid = []
        ct = 0
        oct = 0
        pt = 0

        while base_n + oct < end:
            base_n = base_on_screen + self.chord_y[pt]
            grid.append([oct+base_n,self.notes_rev[pt],pt])
            ct+=1
            pt = ct % len(self.chord_y)
            if pt == 0:
                oct+=self.fuloctave

        base_n = base_on_screen
        ct = -1
        oct = 0
        pt = -1
     #   print(self.chord_y)
        while base_n + oct > start:
         #   print(base_n+oct,start,ct)
           # pt2 = pt
            if pt == len(self.chord_y) - 1:
                oct -= self.fuloctave
            ct -= 1
            pt = ct % len(self.chord_y)
            base_n = base_on_screen + self.chord_y[pt]
            grid.append([oct+base_n,self.notes_rev[pt],pt])
        return grid

@dataclass
class HlineObject:
    coord : List[List[float]]
    key_inf : KeyInf
    str_type : str
    brush : QBrush
    pen: QPen
    label: str = ""
@dataclass
class VlineObject:
    coord : List[List[float]]
    str_type : str
    pen: QPen
    level: int
    label: str = ""
@dataclass
class ChangeLine:
    coord : List[List[float]]
    str_type: str
    pen: QPen
    tempo : float = 0
    tempo_cf : float = 0
    scale : str = 0
    signature : Rational = Rational(4,4)
    label: str = ""

class EdoSync():
    def __init__(self,text):
        self.text = text
class ChangeGrid():
    pitch_wheel_const = 4096
    def __init__(self, time, root_x, root_y,x_step = 50, y_step = 50,**kwargs):
        self.kwargs = kwargs
        self.all_obj = None
        self.edo = 12
        self.oct = 2
        self.count_off_keys = self.edo

        self.parent = kwargs.get('parent',None)
        self.rect = None

        self.only_x = False
        self.only_y = False

        self.time = time
        self.root_x = root_x
        self.root_y = root_y
        self.x_step = x_step
        self.y_step = y_step
        self.signature = Rational(4,4)
        self.num = 1
        self.re_de_num = 2
        self.de_num_mass = [2]
        self.steps = 1

        self.other_lines = True

        self.scale = kwargs.get('scale',None)
        self.is_scale = self.scale is not None and type(self.scale) is Scale

        self.conceptOct = 2
        self.fuloctave = 600
        self.to_rect = 50
        self.block = False
        self.edoe = self.scale is None
        self.keys = None
        self.takt_step = self.signature * 4 * self.x_step
        self.edo_sync = None
        self.auto_keys()
    def simple_to_for_init(self):
        return (self.time,self.root_x,self.root_y,self.x_step,self.y_step,self.kwargs)

    def back_head_rect(self):
        self.rect = HeadRect(change_grid=self, block=self.block)
        self.add_head_rect()

    def add_head_rect(self):
        if self.parent:
            if self.parent.head_scene:
                self.parent.head_scene.addItem(self.rect)

    def get_rect(self):
        return self.rect

    def set_time(self,time):
        self.time = time
        self.root_x = self.time
        self.parent.sort_all()
    def set_head_rect(self,rect):
        self.rect = rect
    def set_edo_sync(self,sync):
        self.edo_sync = sync
    def set_x_step(self,step):
        self.x_step = step
        self.takt_step = self.signature * 4 * self.x_step
    def set_sign(self,sign):
        self.sign = sign
        self.takt_step = self.signature * 4 * self.x_step
    def set_all_obj(self,all_obj):
        self.all_obj = all_obj

    def get_keys(self):
        return self.keys

    def auto_keys(self):
        ## print(self.edoe,self)
        if self.edoe:
            self.keys = KeyData(self.edo,self.conceptOct)
            self.count_off_keys = self.edo
        else:
            self.keys = KeyData(scale = self.scale)
            self.count_off_keys = len(self.scale.chord_y)

    def is_x(self):
        return not self.only_y
    def is_y(self):
        return not self.only_x

    def set_to_rect(self,semitone):
        self.to_rect = semitone / self.pitch_wheel_const
        if self.conceptOct != 2:
            self.fuloctave = self.to_rect * (self.pitch_wheel_const * math.log(self.conceptOct,math.pow(2,1/12)))

    def from_text_edo(self,edo_tex):
        self.edo_sync = EdoSync(edo_tex)
        splited = clear(edo_tex.split('e'))
        if len(splited) >= 1:
            self.edo = int(splited[0])
            if len(splited) == 2:
                self.conceptOct = int(splited[1])
            self.set_to_rect(50)
            self.y_step = self.fuloctave / self.edo
            self.edoe = True
            self.auto_keys()
    def from_edo_sync(self):
        if self.edo_sync:
            edo_tex = self.edo_sync.text
            splited = clear(edo_tex.split('e'))
            if len(splited) >= 1:
                self.edo = int(splited[0])
                if len(splited) == 2:
                    self.conceptOct = int(splited[1])
                self.set_to_rect(50)
                self.y_step = self.fuloctave / self.edo
                self.edoe = True

    def set_only_x(self):
        self.only_x = True
        self.only_y = False
    def set_only_y(self):
        self.only_y = True
        self.only_x = False
    def set_not_only(self):
        self.only_y = False
        self.only_x = False

    def set_parent(self,parent):
        self.parent = parent
        self.add_head_rect()

    def get_snap(self,x,y,index = 0):
        if index == -1:
            if self.parent:
                grid = self.parent.get_grid_ind(self,index)
                return grid.get_snap(x,y)
        if self.is_scale:
            y1 = self.scale.snap_y(y,self.root_y)
        else:
            y1 = round((y-self.root_y) / self.y_step) * self.y_step + self.root_y
        if self.other_lines:
            x1 = round((x-self.root_x) / (self.x_step / self.re_de_num)) * self.x_step / self.re_de_num + self.root_x
        else:
            x1 = round((x-self.root_x) / self.x_step) * self.x_step + self.root_x
        return (x1,y1)

    def get_simp_e(self,i):
        return str(((i - self.root_y) // self.y_step) % self.edo) + "e"

    def get_h_lines(self,start_x,end_x,start_y,end_y):
        h_lines = []
        if self.is_scale:
            mass = self.scale.get_grid(start_y,end_y,self.root_y)
            for l in mass:
                h_lines.append([[start_x,l[0]],[end_x,l[0]],[l[1]]])
        else:
            ofset = int(self.root_y-start_y) % self.y_step
            start_step = int(start_y-self.root_y) // self.y_step
            i = start_y + ofset
            while i < (end_y + ofset):
                h_lines.append([[start_x,i],[end_x,i]])
                i += self.y_step
                start_step += 1
        return h_lines
    def get_color(self):
        if self.only_x:
            return self.parent.color_of_lines.evt_x_pen.color()
        if self.only_y:
            return self.parent.color_of_lines.evt_y_pen.color()
        return self.parent.color_of_lines.evt_pen.color()
    def get_h_lines_colors(self,start_x,end_x,start_y,end_y):
        h_lines = []
        if self.is_scale:
            mass = self.scale.get_grid(start_y,end_y,self.root_y)
            for l in mass:
                index = l[2]
                key_inf = self.keys.get_key_inf(index)
                pen = self.parent.color_of_lines.h_line_pen
                brush = QBrush(self.parent.key_colors.get_back(key_inf.level))
                type = "regular"
                coords = [[start_x,l[0]],[end_x,l[0]]]
                label = l[1]
                h_lines.append(HlineObject(coord = coords,key_inf=key_inf,str_type=type,pen=pen,brush=brush,label=label))
        else:
            ofset = int(self.root_y-start_y) % self.y_step
            ofset2 = int(start_y-self.root_y) % self.y_step
            start_step = int(start_y-self.root_y) // self.y_step
            i = start_y - ofset2
            while i < (end_y + ofset + self.y_step):
                start_step += 1
                key_inf = self.keys.get_key_inf_rev(start_step)
                pen = self.parent.color_of_lines.h_line_pen
                brush = QBrush(self.parent.key_colors.get_back(key_inf.level))
                type = "regular"
                coords = [[start_x,i],[end_x,i]]
                h_lines.append(HlineObject(coord = coords,key_inf=key_inf,str_type=type,pen = pen,brush = brush))
                i += self.y_step

        return h_lines
    def get_v_lines(self,start_x,end_x,start_y,end_y):
        v_lines = []
        i = start_x
        while i < end_x:
            v_lines.append([[i,start_y],[i, end_y],[1]])
            if self.other_lines:
                for k in range(self.re_de_num-1):
                    p = (k+1) * self.x_step / self.re_de_num
                    v_lines.append([[i + p, start_y], [i + p, end_y], [2]])
            i += self.x_step
        return v_lines
    def fill_de_num_mass(self):
        mass = primfacs(self.re_de_num)
        ans = []
        l = 1
        for k in mass:
            l = l*k
            ans.append(l)
        self.de_num_mass = ans
    def set_de_num(self,de_num):
        self.re_de_num = de_num
        self.fill_de_num_mass()


    def get_col_de_num(self):
        k = 1/self.parent.size_factor
        ik = int(k)
        ## print(ik)
        if ik == 0:
            return self.re_de_num
        if ik >= self.re_de_num:
            return 1
        if self.re_de_num % ik == 0:
            return self.re_de_num // ik
        kp = 1
        for p in self.de_num_mass:
            if p > ik:
                return kp
            kp = p
        return kp


    def get_v_lines_colors(self,start_x,end_x,start_y,end_y):
        v_lines = []
        i = start_x
        p = 0
        ct1 = 0
        col_de_num = self.get_col_de_num()
        while i < end_x:
            ct2 = 1
            f = i
            coords = [[i, start_y], [i, end_y]]
            level = 1
            pen = self.parent.color_of_lines.block_pen
            type = "takt"
            v_lines.append(VlineObject(coord=coords, pen=pen, level=level, str_type=type, label=str(ct1)))
            ct1+=0
            while i < f + self.takt_step:
                if ct2 != 0:
                    p = 0
                    coords = [[i, start_y], [i, end_y]]
                    level = 1
                    pen = self.parent.color_of_lines.get_pen(level)
                    type = "regular"
                    v_lines.append(VlineObject(coord = coords,pen=pen,level=level,str_type=type,label=str(ct1) + "." + str(ct2)))
                ct2 += 1
                if self.other_lines:
                    for k in range(col_de_num - 1):
                        p = (k + 1) * self.x_step / col_de_num
                        if i + p >= f + self.takt_step or i + p >= end_x:
                            break
                        coords = [[i + p, start_y], [i + p, end_y]]
                        level = 2
                        pen = self.parent.color_of_lines.get_pen(level)
                        type = "vtor"
                        v_lines.append(VlineObject(coord = coords,pen=pen,level=level,str_type=type,label=""))
                i += self.x_step
                if i + p >= f + self.takt_step or i >= end_x:
                    break
            i = f+self.takt_step
        return v_lines
    def get_grid_colors(self,start_x,end_x,start_y,end_y):
        h_lines = self.get_h_lines_colors(start_x, end_x, start_y, end_y)
        v_lines = self.get_v_lines_colors(start_x, end_x, start_y, end_y)
        return h_lines, v_lines
    def get_grid(self,start_x,end_x,start_y,end_y):
        h_lines = self.get_h_lines(start_x,end_x,start_y,end_y)
        v_lines = self.get_v_lines(start_x,end_x,start_y,end_y)
        return h_lines, v_lines
    def get_text(self):
        if self.is_scale:
            return self.scale.name
        else:
            return str(int(600 / self.y_step * 100)/100)
    def get_onl_text(self):
        if self.only_x:
            return 'x'
        elif self.only_y:
            return 'y'
        return 'xy'
    def grid_line(self,start_y,end_y):
        return [[self.time,start_y],[self.time,end_y],self.get_text(),self.get_onl_text()]
    def grid_line_color(self,start_y,end_y):
        coords = [[self.time,start_y],[self.time,end_y]]
        pen = self.parent.color_of_lines.evt_pen
        type = "all"
        if self.only_x:
            type = "time_sign"
            pen = self.parent.color_of_lines.evt_x_pen
        if self.only_y:
            type = "scale"
            pen = self.parent.color_of_lines.evt_y_pen
        label = ""
        if not self.only_y:
            label += str(self.signature)
        if self.scale is not None and not self.only_x:
            label += self.scale.name
        return ChangeLine(pen=pen,str_type=type,label=label,signature=self.signature,coord = coords)
    def set_root(self,base,i=0):
        if self.is_scale and i != 0:
            self.root_y = base - self.scale.get_coord(i)
        else:
            self.root_y = base
    def set_all(self):
        self.only_y = False
        self.only_x = False
    def set_block(self,block):
        self.block = block

    def __getstate__(self):
        """Возвращает состояние для сериализации"""
        state = self.__dict__.copy()
        # Удаляем несериализуемые атрибуты
        del state['qt_widget']
        del state['temp_data']  # Если не хотим сохранять временные данные
        return state

    def __setstate__(self, state):
        """Восстанавливает состояние после десериализации"""
        self.__dict__.update(state)
        # Восстанавливаем несериализуемые атрибуты значениями по умолчанию
        self.qt_widget = None
        self.temp_data = []
def get_grid_evt_text(x,text,interpr):
    scale = None
    if text in interpr.TempDict.keys():
        scale = Scale(interpr,text)
    if scale is not None:
        event = ChangeGrid(x,x,0,scale=scale)
    else:
        event = ChangeGrid(x,x,0)
        event.from_text_edo(text)
    event.only_y = True
    return event
def get_grid_evt_dialog(x,interpr):
    keys  = list(interpr.TempDict)
    text = show_search_dialog(keys,None,title="Смена сетки")
    if text is not None:
        return get_grid_evt_text(x,text,interpr)
    else:
        return text

def clear_def(mass: List[ChangeGrid]):
    mass_out = []
    for g in mass:
        if g != GridEvents.defGrid:
            mass_out.append(g)
    return mass_out
class GridEvents():
    defGrid = ChangeGrid(0,0,0,50,50)
    def __init__(self, events = [],**kwargs):
        #self.defGrid.set_parent(self)
        self.interpr = None
        if not events:
            events = [get_grid_evt_text(0,"12e",toMidi())]
            events[0].set_all()
            events[0].set_de_num(4)
            events[0].set_x_step(200)
            events[0].set_block(True)

        self.head_scene = None

        self.events = sorted(events,key= lambda x: x.time)
        self.key_colors = KeyColorsObj()
        self.color_of_lines = DefaultColorGrid()
        self.size_factor = 1
        self.ed = 1/4

        for ev in self.events:
            ev.set_parent(self)
    def save_as(self,filename):
        with open(filename + '_grid'+'.pickle', 'wb') as f:
            pickle.dump({"GRID" :self }, f)
    def get_grid_ind(self,ev,index):
        if index == -1:
            ind = self.events[0]
            for i in self.events:
                if i == ev:
                    return ind
                ind = i

    def all_rects(self):
        for ev in self.events:
            ev.back_head_rect()
            rect = ev.get_rect()
            if rect:
                self.head_scene.addItem(rect)
    def set_head_scene(self,scene):
        self.head_scene = scene
        for ev in self.events:
            rect = ev.get_rect()
            if rect:
                self.head_scene.addItem(rect)

    def set_size_factor(self,factor):
        self.size_factor = factor
    def set_grid_colors(self,grid_colors):
        self.color_of_lines = grid_colors
    def set_key_colors(self,key_colors):
        self.key_colors = key_colors
    def set_interpr(self,interpr):
        self.interpr = interpr
    def get_by_time(self,time):
        return self._get_by_time(time)[0]
    def add_grid_evt_text(self,x,text):
        evt = get_grid_evt_text(x,text,self.interpr)
        self.add(evt)
    def dialog_add(self,x):
        evt = get_grid_evt_dialog(x,self.interpr)
        if evt is not None:
            self.add(evt)

    def _get_by_time(self,time):
        for i in range(len(self.events)):
            evt = self.events[len(self.events) - 1 - i]
            if evt.time <= time:
                return (evt,len(self.events) - 1 - i)
        return (self.defGrid,-1)

    def get_all_in_times(self, start, end):
        mass = self._get_by_time(end)
        evt = mass[0]
        grids = []
        grids.append(evt)
        ct = mass[1] - 1
        while ct >= 0 and evt.time >= start:
            evt = self.events[ct]
            grids.append(evt)
            ct-=1
        if ct < 0 and evt.time > start:
            grids.append(self.defGrid)
        return sorted(grids,key= lambda x: x.time)
    def get_ct(self,evt):
        for i in range(len(self.events)):
            if self.events[i] == evt:
                return i
        return -1
    def pred_x(self,evt):
        a = self.get_ct(evt)
        if a != -1:
            a -= 1
            while a >= 0 and not self.events[a].is_x():
                a -= 1
            if a >= 0:
                return self.events[a]
        return self.defGrid
    def pred_y(self,evt):
        a = self.get_ct(evt)
        if a != -1:
            a -= 1
            while a >= 0 and not self.events[a].is_y():
                a -= 1
            if a >= 0:
                return self.events[a]
        return self.defGrid
    def get_norm_x_y(self,start,end):
        grids = self.get_all_in_times(start,end)
        grid_x = []
        grid_y = []
        for grid in grids:
            if grid.is_x():
                grid_x.append(grid)
            if grid.is_y():
                grid_y.append(grid)
        if grid_x[0].time > start and grid_x[0] is not self.defGrid:
            grid_x = self.pred_x(grid_x[0]) + grid_x
        if grid_y[0].time > start and grid_x[0] is not self.defGrid:
            grid_y = self.pred_y(grid_y[0]) + grid_y
        return grid_x,grid_y,grids


    def remove_item(self, item):
        self.events.remove(item)
    def remove(self,time):
        for item in self.events:
            if item.time == time:
                self.events.remove(item)
                break
    def add(self,event):
        event.set_parent(self)
        event.back_head_rect()
        self.events.append(event)
        self.events = sorted(self.events, key=lambda x: x.time)
        if event.only_y or event.only_x:
            for e in range(len(self.events)):
                if self.events[e] == event:
                    if e > 0:
                        if event.only_y:
                            event.set_x_step(self.events[e-1].x_step)
                            event.set_sign(self.events[e-1].signature)
                            event.set_de_num(self.events[e-1].re_de_num)
                        else:
                            if self.events[e-1].scale is not None:
                                event.scale = self.events[e-1].scale
                            else:
                                event.set_edo_sync(self.events[e-1].edo_sync)
                                event.from_edo_sync()
                            event.keys = self.events[e-1].keys
                    return
    def sort_all(self):
        self.events = sorted(self.events, key=lambda x: x.time)

    def get_sep_grid(self,start_x,end_x,start_y,end_y):
        x_y = self.get_norm_x_y(start_x,end_x)
        x_grid = x_y[0]
        y_grid = x_y[1]
        grids = x_y[2]
        h_lines = []
        v_lines = []
        for i in range(len(y_grid)-1):
            grid = y_grid[i].get_h_lines(y_grid[i].time,y_grid[i+1].time,start_y,end_y)
            h_lines = h_lines + grid
        for i in range(len(x_grid) - 1):
            grid = x_grid[i].get_v_lines(x_grid[i].time, x_grid[i + 1].time, start_y, end_y)
            v_lines = v_lines + grid
        gridy = y_grid[-1].get_grid(y_grid[-1].time, end_x, start_y, end_y)
        gridx = x_grid[-1].get_grid(x_grid[-1].time, end_x, start_y, end_y)
        h_lines = h_lines + gridy
        v_lines = v_lines + gridx
        grids_out = []
        for g in grids:
            grids_out.append(g.grid_line(start_y, end_y))
        return h_lines, v_lines, grids_out
    def get_grid(self,start_x,end_x,start_y,end_y):
        grids = self.get_all_in_times(start_x,end_x)
        h_lines = []
        v_lines = []
        if len(grids) == 0:
            return self.defGrid.get_grid(start_x,end_x,start_y,end_y)
        for i in range(len(grids)-1):
            grid = grids[i].get_grid(grids[i].time,grids[i+1].time,start_y,end_y)
            h_lines = h_lines + grid[0]
            v_lines = v_lines + grid[1]
        grid = grids[-1].get_grid(grids[-1].time,end_x,start_y,end_y)
        h_lines = h_lines + grid[0]
        v_lines = v_lines + grid[1]
        grids_out = []
        for g in grids:
            grids_out.append(g.grid_line(start_y,end_y))
        return h_lines, v_lines, grids_out

    def get_grid_colors(self, start_x, end_x, start_y, end_y):
        grids = clear_def(self.get_all_in_times(start_x, end_x))
        #print(grids)
        h_lines = []
        v_lines = []
        if len(grids) == 0:
            return [],[],[]
        for i in range(len(grids) - 1):
            #print(grids[i].time, grids[i + 1].time)
            grid = grids[i].get_grid_colors(grids[i].time, grids[i + 1].time, start_y, end_y)
            h_lines = h_lines + grid[0]
            v_lines = v_lines + grid[1]
        ## print(grids[-1].time, end_x)
        grid = grids[-1].get_grid_colors(grids[-1].time, end_x, start_y, end_y)
        h_lines = h_lines + grid[0]
        v_lines = v_lines + grid[1]
        grids_out = []
        for g in grids:
            grids_out.append(g.grid_line_color(start_y, end_y))
        return h_lines, v_lines, grids_out

    def get_snap(self, x, y, **kwargs):
        time = kwargs.get('time',None)
        base = self._get_by_time(x)[0]
        if time is None:
            return base.get_snap(x,y)
        base2 = self._get_by_time(time)[0]
        return (base.get_snap(x,y)[0],base2.get_snap(x,y)[1])

   # def get_signature_grid(self):


"""scl = Scale(toMidi(),"name",'"name","0 2 0.1 -1 1 -1.1 1.1"')
changeGrids = [get_grid_evt_text(0,"12e",toMidi()),ChangeGrid(200,0,500,scale=scl),ChangeGrid(500,0,0,10,10)]
evts = GridEvents(changeGrids)"""
evts = GridEvents()

class GridScene(QGraphicsScene):
    def drawBackground(self, painter, rect):
        # Сетка 20x20 пикселей
        pen = QPen(QColor(220, 220, 220))
        pen_t = QPen(QColor(242, 242, 242))
        pen2 = QColor(100, 100, 100)
        painter.setPen(pen)
        font = QFont("Arial", 8)
        painter.setFont(font)

        a = int(rect.left())
        b = int(rect.right())
        c = int(rect.bottom())
        d = int(rect.top())
        #print(a,b,d,c)
        lines = evts.get_grid(a,b,d,c)
        h_lines = lines[0]
        v_lines = lines[1]
        # Горизонтальные линии
        #print("h",h_lines)
        #print("v",v_lines)
        for x in v_lines:
            if x[2][0] == 1:
                painter.setPen(pen)
                painter.drawLine(x[0][0],x[0][1],x[1][0],x[1][1])
            elif x[2][0] == 2:
                painter.setPen(pen_t)
                painter.drawLine(x[0][0], x[0][1], x[1][0], x[1][1])
        painter.setPen(pen)
        for y in h_lines:
            #painter.drawLine(rect.left(), y, rect.right(), y)
            painter.drawLine(y[0][0],y[0][1],y[1][0],y[1][1])
            if len(y) > 2:
                painter.setPen(pen2)
               # print(y)
                painter.drawText(y[0][0]+10, y[0][1]-15, y[2][0])
                painter.setPen(pen)
    def drawBackground(self, painter, rect):
        a = int(rect.left())
        b = int(rect.right())
        c = int(rect.bottom())
        d = int(rect.top())
        lines = evts.get_grid_colors(a, b, d, c)
        h_lines = lines[0]
        v_lines = lines[1]
        changes = lines[2]
        last_x = None
        for x in h_lines:
            if last_x is not None:
                painter.setBrush(last_x.brush)
                painter.setPen(QPen(last_x.brush.color()))
                painter.drawRect(last_x.coord[0][0],last_x.coord[0][1],round(x.coord[1][0] - last_x.coord[0][0]), round(x.coord[1][1] -last_x.coord[0][1]))
            last_x = x
        for x in h_lines:
            painter.setPen(x.pen)
            painter.drawLine(x.coord[0][0], x.coord[0][1], x.coord[1][0], x.coord[1][1])
        for y in v_lines:
            painter.setPen(y.pen)
            painter.drawLine(y.coord[0][0], y.coord[0][1], y.coord[1][0], y.coord[1][1])
        for s in changes:
            painter.setPen(s.pen)
            painter.drawLine(s.coord[0][0], s.coord[0][1], s.coord[1][0], s.coord[1][1])




"""
app = QApplication(sys.argv)
scene = GridScene()
scene.setSceneRect(0, 0, 800, 600)

view = QGraphicsView(scene)
view.setWindowTitle("Минимальная сетка")
view.resize(800, 600)
view.show()
sys.exit(app.exec())"""