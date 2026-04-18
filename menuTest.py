from tkinter import *

def dropdown_menu(menu_list):
    root = Tk()
    root.title('Process Mode')
    root.focus()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    appWidth = 200
    appHeight = 100

    root.geometry(f'{appWidth}x{appHeight}+{round((screen_width-appWidth)/2)}+{round((screen_height-appHeight)/2)}')

    tkvar = StringVar(root)
    tkvar.set('Choose Mode')

    def on_selection(value):
        global dropdown_choice
        dropdown_choice = value
        root.destroy()

    popupMenu = OptionMenu(root, tkvar, *menu_list, command=on_selection)
    popupMenu.grid(row=2, column=2)
    popupMenu.config(width=20, height=2)

    root.mainloop()

    return dropdown_choice

options = ['1', '2', '3']

selection = dropdown_menu(options)