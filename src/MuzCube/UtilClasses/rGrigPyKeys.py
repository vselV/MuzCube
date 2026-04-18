from PyQt6.QtGui import QColor



def get_hover_color_hsl(base_color, lightness_change=0.1):
    h, s, l, a = base_color.getHslF()
    if l > 0.5:
        new_lightness = max(0.0, l - lightness_change)
    else:
        new_lightness = min(1.0, l + lightness_change)
    new_color = QColor.fromHslF(h, s, new_lightness, a)
    return new_color
def default_mass():
    mas_colors = []
    mas_colors.append(QColor(255, 255, 255))
    mas_colors.append(QColor(0, 0, 0))
    mas_colors.append(QColor(70, 67, 60))
    mas_colors.append(QColor(127, 119, 90))
    mas_colors.append(QColor(158, 161, 128))
    mas_colors.append(QColor(132, 118, 103))
    mas_colors.append(QColor(112, 109, 99))
    mas_colors.append(QColor(134, 117, 103))
    mas_colors.append(QColor(134, 117, 103))
    return mas_colors
class KeyColorsObj():
    def __init__(self, massive=None):
        if massive is None:
            massive = default_mass()
        self.colors = massive
        self.len = len(massive)
        self.hovered_colors = []
        self.background = []
        for i in range(len(self.colors)):
            self.hovered_colors.append(get_hover_color_hsl(self.colors[i]))
            color = get_hover_color_hsl(self.colors[i],0.4)
            self.background.append(QColor(color.red(),color.green(),color.blue(),60))
    def get_back(self,index):
        return self.background[index%self.len]
    def get_hov(self,index):
        return self.hovered_colors[index%self.len]
    def get_col(self,index):
        return self.colors[index%self.len]
    def get(self,index,hov = False):
        if hov:
            return self.hovered_colors[index%self.len]
        return self.colors[index%self.len]

class KeyInf():
    defoct = 2
    defoct_cent = 1200
    defedo = 12
    def_cent = 100
    minedo = defedo / 16
    mincent = defoct_cent / minedo

    def __init__(self, step, value_cent, edo = 12, oct=2,cent_shir = 0):
        self.step = step
        self.text = ""
        self.edo = edo
        self.value_cent = value_cent
        self.color = 0
        self.level = 0

        self.scaled = False
        self.black = False
        self.vtor_black = False
        self.complete = False
        self.def_width = 0
        if step!=0:
            self.def_width = value_cent / step
        self.width = 0
        self.cent_shir = 0
        self.key_shir = 1

        self.max_level = 1
        self.local_max_level = 1

    def shir_plus(self):
        self.key_shir += 1

    def set_width(self, width):
        self.width = width

    def set_vtor_black(self):
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

    def set_scaled(self, scaled):
        self.scaled = scaled

    def up_shir(self,shir):
        self.cent_shir += shir

    def get_pshir(self):
        return self.cent_shir

def round_to(step1, edo1, edo2):
    step2 = round(step1 * (edo2 / edo1))
    return step2
def round_from_scale(val,edo):
    step2 = round(val / edo)
    return int(step2)

class KeyData():
    strin = "CDEFGAB"
    names7 = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
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
    alters_up = ["#", "↑", "↾", "𝅄", "'"]
    alters_down = ["𝄭", "↓", "⇂", "𝅑", "."]
    list_cents = [70]
    abs_min_delta = 6.6
    x = 50
    for i in range(len(alters_up) - 1):
        x = x / 2
        list_cents.append(x)
    del x


    def __init__(self, edo = 12, oct=defoct, scale = None):

        self.edo = edo
        self.oct = oct
        self.scale = scale

        self.oct_cf = self.oct / self.defoct
        self.pitch_step = self.defoct_cent / self.edo
        self.min_delta = self.pitch_step / 2
        self.min_delta = min(self.abs_min_delta, self.min_delta)
        self.key_dates = []
        self.keys_dict = {}
        if self.scale is None:
            self.fill_keys()
        else:
            self.from_scale()
    def set_color(self, colors):
        self.colors = colors
    def get_key_inf(self,index):
        return self.keys_dict[index%len(self.keys_dict.values())]
    def get_key_inf_rev(self,index):
        return self.keys_dict[(len(self.keys_dict.values())-index) % len(self.keys_dict.values())]
    def get_level(self,i):
        if self.keys_dict.get(i) is not None:
            return self.keys_dict.get(i).level
        return 0
    def from_scale(self):
        key_mass = self.scale.get_all_key_inf()
        for i in self.names7.values():
            tup = self.scale.snap_y(self.scale.convert_pitch(i*self.def_cent),0,return_tup=True)
            ## print(tup,"Sdsdsds")
            i2 = tup[1]
            self.keys_dict[i2] = key_mass[i2]
        for i in range(len(key_mass)):
            if self.keys_dict.get(i) is None:
                self.keys_dict[i] = key_mass[i]
                self.keys_dict[i].set_black(True)
        self.fix_levels()


    def to_edo(self, step):
        return round_to(step, self.defedo, self.edo)

    def out_edo(self, step):
        return round_to(step, self.edo, self.defedo)

    def val_cent(self, step):
        return self.pitch_step * self.oct_cf * step

    def get_text(self, step):
        out = self.out_edo(step)
        if out not in self.denum:
            return str(step)
        text = self.denum[out]
        delta = step * self.pitch_step - out * self.def_cent
        ct = 0
        for t in self.list_cents:
            if abs(delta) < self.min_delta:
                break
            if abs(delta) < t:
                continue
            if delta < 0:
                delta += t
                if ct < len(self.alters_up):
                    text += self.alters_up[ct]
            else:
                delta -= t
                if ct < len(self.alters_down):
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
        if self.edo >= self.defedo:
            self.first_fill_keys()
            for i in range(self.edo):
                if self.keys_dict.get(i) is None:
                    self.keys_dict[i] = KeyInf(i, self.val_cent(i), self.edo, self.oct)
                    self.keys_dict[i].set_vtor_black()
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
        if self.scale is not None:
            self.edo = len(self.keys_dict.values())
        for i in range(self.edo):

            if self.keys_dict[i].is_white():
                ct = 0
                cur_blacs = []
                continue

            ct += 1
            for k in cur_blacs:
                k.shir_plus()
                k.up_shir(self.keys_dict[i].get_pshir())
                k.local_max_level = ct
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
        for i in range(self.edo):
            self.keys_dict[i] = KeyInf(i, self.val_cent(i), self.edo, self.oct)
            self.keys_dict[i].set_text(str(self.strin[i % len(self.strin)]))
            self.keys_dict[i].comp()

    def fill10edo(self):
        for i in range(self.edo):
            self.keys_dict[i] = KeyInf(i, self.val_cent(i), self.edo, self.oct)
            if i % 2 == 1:
                self.keys_dict[i].set_black(True)
                self.keys_dict[i].set_text(str(self.strin[i // 2]) + "#")
            else:
                self.keys_dict[i].set_text(str(self.strin[i // 2]))
            self.keys_dict[i].comp()