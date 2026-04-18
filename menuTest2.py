import tkinter as tk

class RightClickMenu:
    def __init__(self, master):
        self.master = master
        master.title("Right-Click Menu Example")

        # Create a label (or any widget you want)
        self.label = tk.Label(master, text="Right-click here!", padx=20, pady=20)
        self.label.pack()

        # Bind the right mouse button to the `show_menu` function
        self.label.bind("<Button-3>", self.show_menu)  # Button-3 is the right mouse button

        # Create the menu
        self.menu = tk.Menu(master, tearoff=0)  # tearoff=0 removes the dashed line at the top

        # Add menu items
        self.menu.add_command(label="Option 1", command=self.option1_selected)
        self.menu.add_command(label="Option 2", command=self.option2_selected)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=master.quit)

    def show_menu(self, event):
        """Displays the context menu at the location of the right-click."""
        try:
            self.menu.tk_popup(event.x_root, event.y_root) # Popup at root coordinates
        finally:
            self.menu.grab_release() # Release the grab (important!)


    def option1_selected(self):
        """Action to perform when Option 1 is selected."""
        print("Option 1 selected!")
        # You can add any logic here, such as updating a label, opening a dialog, etc.
        self.label.config(text="Option 1 was clicked!")


    def option2_selected(self):
        """Action to perform when Option 2 is selected."""
        print("Option 2 selected!")
        self.label.config(text="Option 2 was clicked!")


root = tk.Tk()
my_gui = RightClickMenu(root)
root.mainloop()