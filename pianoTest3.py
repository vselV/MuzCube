import tkinter as tk
from tkinter import ttk
import math

class Note:
    def __init__(self, x, y, width=40, height=20, velocity=100):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity = velocity
        self.text_note = ""
        self.id = None  # Canvas ID for visualization
        self.resize_id = None  # Canvas ID for resize handle
        self.text_id = None
        self.last_x = x
        self.last_y = y
        self.offset_x = 0
        self.offset_y = 0
        self.exist = False
        self.change_text = True
    def set_text_note(self,text):
        self.text_note = text
        self.change_text = True
class Grid:
    def __init__(self):
        self.vertical = []
class PianoRollCanvas(tk.Canvas):
    def __init__(self, master, width=800, height=400,**kwargs):
        super().__init__(master, width=width, height=height)
        self.default_note_handle=5

        self.width = width
        self.height = height

        self.grid_in_beats=0
        self.special_vertical_grid=[]
        self.special_horizontal_grid=[]

        #меню для ноты где можно писать текст

        self.notes = []
        self.dragging = False
        self.resizing = False
        self.current_note = None
        self.last_x = 0  # Initialize last_x
        self.last_y = 0  # Initialize last_y
        self.resize_dict = {}
        self.id_dict = {}

        # Bind events
        self.bind('<Button-1>', self.handle_left_click)
        self.bind('<Button-3>', self.handle_right_click)

        self.bind('<B1-Motion>', self.handle_mouse_motion)
        self.bind('<B3-Motion>', self.handle_mouse_motion_B3)
        self.bind('<ButtonRelease-1>', self.handle_left_release)

        # Drawing settings
        self.note_color = kwargs.get("note_color1",'#4488ff')
        self.resize_handle_color = kwargs.get("note_color1",'red')
        self.note_text_color = kwargs.get("note_text_color",'green')
        self.line_color = kwargs.get("line_color",'#000000')

        self.delete_mouse=False

        self.menu = tk.Menu(master, tearoff=0)
        self.menu.add_command(label="Set Note", command=self.set_note)

        self.for_text = tk.Entry()

        self.pose_click_x = 0
        self.pose_click_y = 0
    def draw_background(self):
        # Clear canvas
        self.delete("line")

        # Draw subtle background grid for reference
        for x in range(0, self.width, 50):
            self.create_line(x, 0, x, self.height, fill = self.line_color,tags=("line",))
        for y in range(0, self.height, 30):
            self.create_line(0, y, self.width, y, fill = self.line_color,tags=("line",))
        self.tag_lower("line")

        # Draw notes
        for note in self.notes:
            self._draw_note(note)
    def _draw_note(self, note):
        if note.exist:
            self.moveto(note.id, note.x, note.y)
            self.moveto(note.resize_id, note.x + note.width - self.default_note_handle, note.y)
            #if note.change_text:
             #   self.delete(note.text_id)
               # note.text_id = self.create_text(200, 150, text="Hello, Tkinter!", font=("Arial", 24), fill="blue")
        else:
            # Draw note rectangle
            note.id = self.create_rectangle(
                note.x, note.y,
                note.x + note.width, note.y + note.height,
                fill=self.note_color
            )
            self.id_dict[note.id] = note
            # Draw resize handle
            note.resize_id = self.create_rectangle(
                note.x + note.width - self.default_note_handle, note.y,
                note.x + note.width, note.y + note.height,
                fill=self.resize_handle_color
            )
            self.id_dict[note.resize_id] = note
            self.resize_dict[note.resize_id] = note
            note.exist = True
    def _delete_note(self, note):
        self.id_dict[note.id] = None
        self.id_dict[note.resize_id] = None
        self.resize_dict[note.resize_id] = None
        self.delete(note.id,note.resize_id,note.text_id)
        self.notes.remove(note)
    def handle_left_click(self, event):
        # Check if clicking on existing note or resize handle
        items = self.find_withtag("current")
        if items:
            # Get the associated note
            for item in items:
                if self.id_dict.get(item) is not None:
                    self.current_note = self.id_dict.get(item)
                    self.current_note.offset_x = event.x-self.current_note.x
                    self.current_note.offset_y = event.y-self.current_note.y
                    if self.resize_dict.get(item) is not None:
                        self.resizing = True
                    else:
                        self.dragging = True
        else:
        # Create new note at click position
            self.current_note = Note(event.x, event.y)
            self.notes.append(self.current_note)
            self.id_dict[self.current_note.resize_id] = self.current_note
            self.id_dict[self.current_note.id] = self.current_note
            self.resize_dict[self.current_note.resize_id] = self.current_note
        self.dragging = True
        self.draw_background()

    def handle_right_click(self, event):
        items = self.find_withtag("current")
        if items:
            self.delete_mouse = False
            for item in items:
                if self.id_dict.get(item) is not None:
                    self.current_note = self.id_dict.get(item)
                    self.pose_click_x = event.x
                    self.pose_click_y = event.y
            try:
                self.menu.tk_popup(event.x_root, event.y_root) # Popup at root coordinates
            finally:
                self.menu.grab_release() # Release the grab (important!)
        else:
            self.delete_mouse = True
    def handle_mouse_motion(self, event):
        if not self.current_note:
            return
        if self.dragging:
            # Update note position
            dx = event.x - self.current_note.last_x
            dy = event.y - self.current_note.last_y
            self.current_note.x += dx - self.current_note.offset_x
            self.current_note.y += dy - self.current_note.offset_y
            self.current_note.last_x = event.x - self.current_note.offset_x
            self.current_note.last_y = event.y - self.current_note.offset_y
        elif self.resizing:
            # Update note width
            self.current_note.width = max(10, event.x - self.current_note.x)
        self.draw_background()

    def handle_mouse_motion_B3(self, event):
        if self.delete_mouse:
            items = self.find_overlapping(event.x,event.y,event.x+1,event.y+1)
            for item in items:
                if self.id_dict.get(item) is not None:
                    self._delete_note(self.id_dict.get(item))
        self.draw_background()
    def handle_left_release(self, event):
        self.dragging = False
        self.resizing = False
        self.current_note = None

    def handle_right_release(self, event):
        self.delete_mouse = False
    def set_note_bind(self,entry,win):
        self.current_note.set_text_note(entry.get())
        win.destroy()
    def set_note(self):
        win=tk.Toplevel()
        win.geometry("+%d+%d" % (self.winfo_rootx() + self.pose_click_x, self.winfo_rooty() + self.pose_click_y))
        win.overrideredirect(1)
        entry = tk.Entry(win)
        entry.pack()
        win.bind("<Escape>",lambda event: win.destroy())
        win.bind("<Return>",lambda event: self.set_note_bind(entry,win))
class PianoRollEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Free Movement Piano Roll Editor")

        # Create main frame
        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.pack( expand=True)
        # Create piano roll canvas
        self.canvas = PianoRollCanvas(self.frame)
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        # Configure grid weights
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

        # Initial draw
        self.canvas.draw_background()

    def run(self):
        self.root.mainloop()

# Create and run the editor
editor = PianoRollEditor()
editor.run()