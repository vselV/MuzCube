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
        self.id = None  # Canvas ID for visualization
        self.resize_id = None  # Canvas ID for resize handle

class PianoRollCanvas(tk.Canvas):
    def __init__(self, master, width=800, height=400):
        super().__init__(master, width=width, height=height)

        self.width = width
        self.height = height
        self.notes = []
        self.dragging = False
        self.resizing = False
        self.current_note = None

        # Bind events
        self.bind('<Button-1>', self.handle_left_click)
        self.bind('<B1-Motion>', self.handle_mouse_motion)
        self.bind('<ButtonRelease-1>', self.handle_left_release)

        # Drawing settings
        self.note_color = '#4488ff'
        self.resize_handle_color = 'red'

    def draw_background(self):
        # Clear canvas
        self.delete("all")

        # Draw subtle background grid for reference
        for x in range(0,50, self.width):
            self.create_line(x, 0, x, self.height, fill='#f0f0f0')
        for y in range(0,30, self.height):
            self.create_line(0, y, self.width, y, fill='#f0f0f0')

        # Draw notes
        for note in self.notes:
            self._draw_note(note)

    def _draw_note(self, note):
        # Draw note rectangle
        note.id = self.create_rectangle(
            note.x, note.y,
            note.x + note.width, note.y + note.height,
            fill=self.note_color
        )

        # Draw resize handle
        note.resize_id = self.create_rectangle(
            note.x + note.width - 5, note.y,
            note.x + note.width, note.y + note.height,
            fill=self.resize_handle_color
        )

    def handle_left_click(self, event):
        # Check if clicking on existing note or resize handle
        item = self.find_withtag("current")
        if item:
            # Get the associated note
            for note in self.notes:
                if note.id in item or note.resize_id in item:
                    self.current_note = note
                    # Determine if resizing
                    if note.resize_id in item:
                        self.resizing = True
                    else:
                        self.dragging = True
                    break
            return

        # Create new note at click position
        self.current_note = Note(event.x, event.y)
        self.notes.append(self.current_note)
        self.dragging = True

        self.draw_background()

    def handle_mouse_motion(self, event):
        if not self.current_note:
            return

        if self.dragging:
            # Update note position
            dx = event.x - self.last_x
            dy = event.y - self.last_y
            self.current_note.x += dx
            self.current_note.y += dy
        elif self.resizing:
            # Update note width
            self.current_note.width = max(10, event.x - self.current_note.x)

        self.last_x = event.x
        self.last_y = event.y

        self.draw_background()

    def handle_left_release(self, event):
        self.dragging = False
        self.resizing = False
        self.current_note = None

class PianoRollEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Free Movement Piano Roll Editor")

        # Create main frame
        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

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