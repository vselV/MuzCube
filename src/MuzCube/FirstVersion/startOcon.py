import tkinter as tk
from tkinter import ttk
from tkinter import *
import texTabGraphics
from pathlib import Path
def startOcon():
    Path=""
    start = Tk()
    start.title("выбери фаил")
    start.geometry("250x100")
    def get():
        nonlocal Path
        Path = entry.get()     # получаем введенный текст
        start.destroy()
    label=ttk.Label(text="Выберете папку с текстовыми файлами:")
    label.pack()
    textVar=tk.StringVar()
    textVar.set("music")
    entry = ttk.Entry(width=45,textvariable=textVar)
    entry.pack(anchor=NW, padx=8, pady= 8)
    btn = ttk.Button(text="Готово", command=get)
    btn.pack()
    label = ttk.Label()
    label.pack(anchor=NW, padx=6, pady=6)
    start.mainloop()
    return Path
def textOcon():
    Path=""
    start = Tk()
    start.title("выбери фаил")
    start.geometry("250x200")
    def get():
        nonlocal Path
        print(entry.get())
        Path = entry.get()     # получаем введенный текст
        print(Path)
        start.destroy()
    entry = ttk.Entry()
    entry.pack(anchor=NW, padx=8, pady= 8)
    btn = ttk.Button(text="Click", command=get)
    btn.pack(anchor=NW, padx=6, pady=6)
    label = ttk.Label()
    label.pack(anchor=NW, padx=6, pady=6)
    start.mainloop()
    return Path
pat=startOcon()
print(pat)
Path(pat).mkdir(parents=True, exist_ok=True)
texTabGraphics.init(pat)