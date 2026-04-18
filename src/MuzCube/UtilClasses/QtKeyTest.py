from pickle import encode_long

from PyQt6.QtCore import Qt
from pygame.examples.testsprite import flags
import copy
def clear(mass):
    out = []
    for s in mass:
        if s != "":
            out.append(s)
    return out
def create_filtered_qt_key_dict():
    """Создает отфильтрованный словарь ключей"""
    key_dict = {}

    # Только реальные клавиши (исключаем модификаторы и специальные значения)
    key_attributes = [
        'Key_0', 'Key_1', 'Key_2', 'Key_3', 'Key_4', 'Key_5', 'Key_6', 'Key_7', 'Key_8', 'Key_9',
        'Key_A', 'Key_B', 'Key_C', 'Key_D', 'Key_E', 'Key_F', 'Key_G', 'Key_H', 'Key_I', 'Key_J',
        'Key_K', 'Key_L', 'Key_M', 'Key_N', 'Key_O', 'Key_P', 'Key_Q', 'Key_R', 'Key_S', 'Key_T',
        'Key_U', 'Key_V', 'Key_W', 'Key_X', 'Key_Y', 'Key_Z',
        'Key_Space', 'Key_Enter', 'Key_Return', 'Key_Tab', 'Key_Backspace', 'Key_Delete',
        'Key_Escape', 'Key_CapsLock', 'Key_Shift', 'Key_Control', 'Key_Alt', 'Key_Meta',
        'Key_Left', 'Key_Right', 'Key_Up', 'Key_Down',
        'Key_F1', 'Key_F2', 'Key_F3', 'Key_F4', 'Key_F5', 'Key_F6',
        'Key_F7', 'Key_F8', 'Key_F9', 'Key_F10', 'Key_F11', 'Key_F12'
    ]

    for attr_name in key_attributes:
        if hasattr(Qt.Key, attr_name):
            attr_value = getattr(Qt.Key, attr_name)
            key_name = attr_name.replace('Key_', '').replace('_', ' ').title()
            key_dict[key_name] = attr_value

    return key_dict


def create_mouse_buttons_dict():
    """Создает словарь для кнопок мыши"""
    mouse_buttons_dict = {}

    button_attributes = [
        'LeftButton', 'RightButton', 'MiddleButton',
        'BackButton', 'ForwardButton', 'TaskButton',
        'ExtraButton4', 'ExtraButton5', 'ExtraButton6',
        'ExtraButton7', 'ExtraButton8', 'ExtraButton9',
        'ExtraButton10', 'ExtraButton11', 'ExtraButton12',
        'ExtraButton13', 'ExtraButton14', 'ExtraButton15',
        'ExtraButton16', 'ExtraButton17', 'ExtraButton18',
        'ExtraButton19', 'ExtraButton20', 'ExtraButton21',
        'ExtraButton22', 'ExtraButton23', 'ExtraButton24'
    ]

    for attr_name in button_attributes:
        if hasattr(Qt.MouseButton, attr_name):
            attr_value = getattr(Qt.MouseButton, attr_name)
            button_name = attr_name.replace('Button', '').replace('_', ' ').title()
            mouse_buttons_dict[button_name] = attr_value

    return mouse_buttons_dict
full_mouse_dict = create_mouse_buttons_dict()
full_key_dict = create_filtered_qt_key_dict()

class KeyBind():
    def __init__(self, str_val, bind, super = True):
        self.bol = {"Control": False, "Shift": False, "Alt": False}
        self.key = 0
        self.from_str_val(str_val)
        self.bind = bind
        self.super = super
    def from_str_val(self,str_val):
        split = str_val.split('_')
        for s in split:
            if self.bol.get(s) is not None:
                self.bol[s] = True
            else:
                self.key = full_key_dict.get(s)
    def check(self, event, bols):
        if event == self.key and self.bol == bols:
            return True
        return False
    def press(self, event, bols):
        ans = self.check(event, bols)
        if ans:
            self.bind()
        return ans
class KeyManage():
    def __init__(self):
        self.bol = {"Control": False, "Shift": False, "Alt": False}
        self.dictEvt = {Qt.Key.Key_Control: "Control", Qt.Key.Key_Shift:  "Shift", Qt.Key.Key_Alt: "Alt"}
        self.key_binds = {}
        self.accept = True
        self.super = True
    def ctrl(self):
        return self.bol["Control"]
    def alt(self):
        return self.bol["Alt"]
    def shift(self):
        return self.bol["Shift"]
    def sup(self):
        return self.super
    def add_state(self,key):
        self.bol[key] = False
    def add_key_bind(self, str_val,bind,sup=True):
        self.key_binds[str_val] = KeyBind(str_val, bind, sup)
    def KeyPress(self,event):
        self.super = True
        #print("noK")
        if self.dictEvt.get(event.key()) is not None:
            self.bol[self.dictEvt[event.key()]] = True
            print("none",self.bol[self.dictEvt[event.key()]],self.dictEvt[event.key()])
        for bind in self.key_binds.values():
            if bind.press(event.key(), self.bol):
                self.super = bind.super
                break
        if self.accept:
            event.accept()
    def KeyRelease(self,event):
        if self.dictEvt.get(event.key()) is not None:
            print("none", self.bol[self.dictEvt[event.key()]], self.dictEvt[event.key()])
            self.bol[self.dictEvt[event.key()]] = False
        if self.accept:
            event.accept()
class MouseRegime():
    left_button = ["all","draw", "fill"]
    right_button = ["all","delete", "select"]
    body_head = ["all","body","head"]
    def __init__(self,left="all",right ="all",body_head="all"):
        self.left_regime = left
        self.right_regime = right
        self.body_head = body_head
    def is_flag(self,flag):
        if flag == "all": return True
        return self.left_regime == flag or self.right_regime == flag

    def set_left_flag(self,flag):
        self.left_regime = flag
    def set_right_flag(self,flag):
        self.right_regime = flag

    def set_flag(self,flag):
        if flag in self.left_button:
            self.left_regime = flag
        else:
            self.right_regime = flag
class MouseBind():
    bol = {"Control": False, "Shift": False, "Alt": False}

    def __init__(self, button, flag):
        self.states_dict = {}

        self.regime = None
        self.button = button
        self.flag = flag

        self.pressed = False
        self.move = False

        self.bind_dict = {}
        self.bind_bool = None
        self.def_dict = {"press": self.MousePress,"move" : self.MouseMove,"release": self.MouseRelease ,"double_click": self.DoubleClick}
        self.regime = None
        self.sup_dict = {}
        self.ans = False

    def set_states_dict(self,dict):
        self.states_dict = dict

    def set_bol(self,states):
        self.bind_bool = copy.copy(self.bol)
        for state in states:
            self.bind_bool[state] = True

    def set_sup_evt(self,evt,sup):
        self.sup_dict[evt] = sup
    def get_sup_evt(self,evt):
        if self.sup_dict.get(evt) is not None:
            return self.sup_dict[evt]
        return True
    def set_regime(self, regime):
        self.regime = regime
    def add_bind(self,evt,bind):
        self.bind_dict[evt] = bind
    def triger_bind(self,evt,event):
        if self.bind_dict.get(evt) is not None:
            self.bind_dict[evt](event)
            self.ans = True
    def regime_triger(self,evt,event):
        if self.button == event.button() or (evt == "move" and self.pressed):
            if self.bind_bool is None:
                if self.regime is None:
                    self.triger_bind(evt,event)
                    return True
                else:
                    if self.regime.is_flag(self.flag):
                        self.triger_bind(evt,event)
                        return True
            else:
                if self.states_dict == self.bind_bool:
                    if self.regime is None:
                        self.triger_bind(evt, event)
                        return True
                    else:
                        if self.regime.is_flag(self.flag):
                            self.triger_bind(evt, event)
                            return True
        return False
    def MousePress(self,event):
        if self.regime_triger("press", event):
            self.move = False
            self.pressed = True
            return True
        return False
    def MouseMove(self,event):
        if self.regime_triger("move", event):
            self.move = True
            return True
        return False
    def MouseRelease(self,event):
        if self.regime_triger("release", event):
            if not self.move:
                self.triger_bind("click",event)
            self.pressed = False
            self.move = False
            return True
        return False
    def DoubleClick(self,event):
        return self.regime_triger("double_click",event)
    def auto_def(self,evt,event):
        self.def_dict[evt](event)
        bol_ans = self.ans
        self.ans = False
        return (bol_ans,self.get_sup_evt(evt))
    def ghost_move(self):
        self.move = True


class MouseManage():
    possible_evt = ["press","move","release","click","double_click"]

    def __init__(self):
        self.states_dict = None

        self.mouse_binds = {}
        self.mouse_his = []

        self.equal_lines = 0

        self.regime = MouseRegime()
    def set_states_dict(self,dict):
        self.states_dict = dict

    def add_mouse_bind(self,str_val,evt,bind,sup = True):
        if self.mouse_binds.get(str_val) is None:
            val = str_val.split('-')
            split = val[0].split('_')
            button = full_mouse_dict[split[0]]
            flag = "all"
            if len(split) == 2:
                flag = split[1]
            self.mouse_binds[str_val] = MouseBind(button,flag)
            self.mouse_binds[str_val].set_regime(self.regime)
            if self.states_dict is not None:
                self.mouse_binds[str_val].set_states_dict(self.states_dict)
                if len(val) == 2:
                    states = val[1].split("_")
                    self.mouse_binds[str_val].set_bol(states)
        if evt in self.possible_evt:
            self.mouse_binds[str_val].add_bind(evt,bind)
            self.mouse_binds[str_val].set_sup_evt(evt,sup)

    def auto_def(self,evt,event):
        out = True
        for bind in self.mouse_binds.values():
            ans = bind.auto_def(evt,event)
            if ans[0]: out = ans[1]
        return out
    def ghost_move(self):
        for bind in self.mouse_binds.values():
            bind.ghost_move()
    def set_flag(self,flag):
        self.regime.set_flag(flag)
    def set_left_flag(self,flag):
        self.regime.set_left_flag(flag)
    def set_right_flag(self,flag):
        self.regime.set_right_flag(flag)
    def set_regime(self,regime):
        self.regime = regime

class DrawMouseManage(MouseManage):
    def __init__(self):
        super().__init__()
        self.set_flag("draw")
        self.set_flag("delete")

class AllEventManager():
    def __init__(self):
        self.mouse_manager = DrawMouseManage()
        self.key_manager = KeyManage()
        self.regime = self.mouse_manager.regime
        self.mouse_manager.set_states_dict(self.key_manager.bol)
    def add_mouse_bind(self,str_val,evt,bind,sup = True):
        self.mouse_manager.add_mouse_bind(str_val,evt,bind,sup)
    def add_key_bind(self,str_val,bind,sup = True):
        self.key_manager.add_key_bind(str_val,bind,sup)
    def auto_def(self,evt,event):
        return self.mouse_manager.auto_def(evt,event)
    def KeyPress(self,event):
        self.key_manager.KeyPress(event)
    def KeyRelease(self,event):
        self.key_manager.KeyRelease(event)
    def set_flag(self,flag):
        self.regime.set_flag(flag)
    def sup(self):
        return self.key_manager.sup()
    def ghost_move(self):
        self.mouse_manager.ghost_move()
    def ctrl(self):
        return self.key_manager.ctrl()
    def alt(self):
        return self.key_manager.alt()
    def shift(self):
        return self.key_manager.shift()

# Использование
#filtered_dict = create_filtered_qt_key_dict()
#for key, value in filtered_dict.items():
#    print(f"{key}: {value}")