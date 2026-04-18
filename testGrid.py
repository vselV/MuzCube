from tkinter import *
from tkinter import ttk

root = Tk()
root.title("METANIT.COM")
root.geometry("250x200")

for c in range(3): root.columnconfigure(index=c, weight=1)
for r in range(3): root.rowconfigure(index=r, weight=1)

for r in range(3):
    for c in range(3):
        btn = ttk.Button(text=f"({r},{c})")
     #   btn.grid(row=r, column=c, ipadx=6, ipady=6, padx=4, pady=4, sticky=NSEW)
        btn.grid(row=r, column=c, ipadx=6, ipady=6, padx=4, pady=4)

root.mainloop()