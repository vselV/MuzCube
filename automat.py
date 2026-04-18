from PyQt6.QtGui import QTextLine, QTextTable
from PyQt6.QtWidgets import QWidget, QGridLayout, QApplication, QGraphicsTextItem, QLineEdit, QVBoxLayout, QPushButton
import sys
import time

from OpenGlClear import state

alphabet =["0","1","2"]
states = ["a","b","c"]
stat = {"a":0,"b":1,"c":2}

one_tab = []
two_tab = []

func = {}

def left(c):
    c[0] = c[0] - 1
def right(c):
    c[0] = c[0] + 1
def up(c):
    c[1] = c[1] + 1
def down(c):
    c[1] = c[1] - 1

dictf = {"<" : left,">": right ,"^":up,"_":down}
deicts = {}
def f1(mass, cord, out, function):
    mass[cord[0]][cord[1]] = out
    function(cord)


mass = []
for i in range(100):
    mass.append([])
    for j in range(100):
        mass[i].append(0)
mass[50][50] = 1

def interprit(chord,mass,mass2rul,state = "a"):
    chord2 = [stat[state]][mass[chord[0]][chord[1]]]
    text = mass2rul[chord2[0]][chord2[1]]
    change_val = int(text[0])
    func = dictf[str(text[1])]
    new_state = str(text[2])
    f1(mass,chord,change_val,func)
    return new_state
def printMass(mass):
    for i in range(len(mass)):
        for j in range(len(mass[i])):
            if mass[i][j] == 0:
                print(" ",end="")
            elif mass[i][j] == 1:
                print(".", end="")
            else:
                print("_", end="")
        print()

def allInter(chord,mass,mass2rul,state = "a"):
    printMass(mass)
    state = state
    for i in range(5):
        time.sleep(300)
        state = interprit(chord,mass,mass2rul,state)

class ToolbarSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.a= QWidget()
        self.b = QVBoxLayout(self.a)
        self.but = QPushButton("Button 1")
        self.but.clicked.connect(self.interprButton)
        self.b.addWidget(self.but)
        self.grid_layout = QGridLayout(self.a)
        self.grid_layout.setSpacing(1)  # Минимальный промежуток между иконками
        self.grid_layout.setContentsMargins(1, 1, 1, 1)  # Минимальные отступы
        self.setLayout(self.grid_layout)
        self.items = []
        for i in range(10):
            self.items.append([])
            for j in range(10):
                text = ""
                if i == 0 and j >= 1 and j <= len(alphabet):
                    text = alphabet[j-1]
                elif j == 0 and i >= 1 and i <= len(states):
                    text = states[i - 1]
                w = QLineEdit(text)
                self.grid_layout.addWidget(w,i,j)
                self.items.append(w)
        self.grid_layout.addWidget(self.but, 0, 0)
    def add_item(self, item, row=None, col=None):
        if row is None:
            row = self.current_row
        if col is None:
            col = self.current_col
        self.grid_layout.addWidget(item, row, col)
        self.items[(row, col)] = item
        return item
    def get_mass_text(self):
        mass = []
        for i in range(1,10):
            mass.append([])
            for j in range(1,10):
                mass[i].append(self.items[i][j])
        return mass
    def interprButton(self):
        mass2 = self.get_mass_text()
        allInter([50,50],mass,mass2)

app = QApplication(sys.argv)
window = ToolbarSection(None)
window.show()
sys.exit(app.exec())
