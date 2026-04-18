import tkinter as tk
import src.MuzCube.Lex.MuzCubeLexer
from chlorophyll import CodeView
root = tk.Tk()
codeview = CodeView(root, lexer=MuzCubeLexer.MuzCubeLexer, color_scheme="arduino")
codeview.insert("1.0",open("./music/seria.txt").read())
codeview.pack(fill="both", expand=True)
root.mainloop()