import colorsys
import tkinter as tk
import time

def toStrRgb(mass):
    return [int(mass[0]*255),int(mass[1]*255),int(mass[2]*255)]

rt=tk.Tk()
for i in range(12):
    a=colorsys.hsv_to_rgb(float(i)/12, 0.5, 0.5)
    b=toStrRgb(a)
    print(b)
    print('#%02x%02x%02x' % (b[0], b[1], b[2]))
   # time.sleep(1)
    g=tk.Entry(foreground='#%02x%02x%02x' % (b[0], b[1], b[2]),background='#%02x%02x%02x' % (b[0], b[1], b[2]))
    g.pack()
rt.mainloop()
