import tkinter as tk
from tkinter import ttk
import numpy as np

class Note:
    def __init__(self, start_time, duration, pitch, velocity=100):
        self.start_time = start_time
        self.duration = duration
        self.pitch = pitch
        self.velocity = velocity
        self.id = None  # Canvas ID for visualization

class PianoRollCanvas(tk.Canvas):
    def __init__(self, master, width=800, height=400):
        super().__init__(master, width=width, height=height)

        self.width = width
        self.height = height
        self.notes = []
        self.current_note = None
        self.dragging = False
        self.resize_handle = None

        # Bind events
        self.bind('<Button-1>', self.handle_left_click)
        self.bind('<B1-Motion>', self.handle_mouse_motion)
        self.bind('<ButtonRelease-1>', self.handle_left_release)

    def draw_grid(self):
        # Clear canvas
        self.delete("all")

        # Draw vertical lines (time divisions)
        cell_width = self.width // 16  # 16th notes
        for x in range(0, self.width + 1, cell_width):
            self.create_line(x, 0, x, self.height)

        # Draw horizontal lines (note divisions)
        cell_height = self.height // 12  # One octave
        for y in range(0, self.height + 1, cell_height):
            self.create_line(0, y, self.width, y)

        # Draw notes
        for note in self.notes:
            x1 = int(note.start_time * cell_width)
            y1 = int(note.pitch * cell_height)
            x2 = int((note.start_time + note.duration) * cell_width)
            y2 = int((note.pitch + 1) * cell_height)

            # Draw note rectangle
            note.id = self.create_rectangle(x1, y1, x2, y2, fill='#4488ff')

            # Add resize handle
            self.add_resize_handle(note)

    def add_resize_handle(self, note):
        x1 = int((note.start_time + note.duration) * (self.width / 16))
        y1 = int(note.pitch * (self.height / 12))
        x2 = x1 + 5
        y2 = int((note.pitch + 1) * (self.height / 12))
        note.resize_id = self.create_rectangle(x1, y1, x2, y2, fill='red')

    def handle_left_click(self, event):
        grid_x = int(event.x / (self.width / 16))  # Convert to 16th notes
        grid_y = int(event.y / (self.height / 12))  # Convert to semitones

        # Check if clicking on existing note
        for note in self.notes:
            x1 = int(note.start_time * (self.width / 16))
            y1 = int(note.pitch * (self.height / 12))
            x2 = int((note.start_time + note.duration) * (self.width / 16))
            y2 = int((note.pitch + 1) * (self.height / 12))

            if (x1 <= event.x <= x2 and
                    y1 <= event.y <= y2):
                self.current_note = note
                self.dragging = True
                return

        # Create new note
        self.current_note = Note(grid_x, 1, grid_y)
        self.notes.append(self.current_note)
        self.draw_grid()

    def handle_mouse_motion(self, event):
        if self.dragging and self.current_note:
            grid_x = int(event.x / (self.width / 16))
            if grid_x >= 0:
                self.current_note.start_time = grid_x
                self.draw_grid()

    def handle_left_release(self, event):
        self.dragging = False
        self.current_note = None

class PianoRollEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Piano Roll Editor")

        # Create main frame
        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create piano roll canvas
        self.canvas = PianoRollCanvas(self.frame)
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create velocity control
        self.velocity_var = tk.IntVar(value=100)
        self.velocity_scale = ttk.Scale(
            self.frame,
            from_=1,
            to=127,
            variable=self.velocity_var,
            orient=tk.HORIZONTAL,
        )
        self.velocity_scale.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        # Configure grid weights
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

        # Initial draw
        self.canvas.draw_grid()

    def run(self):
        self.root.mainloop()

# Create and run the editor
editor = PianoRollEditor()
editor.run()