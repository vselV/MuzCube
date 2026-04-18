
import tkinter as tk
from tkinter import ttk
import math

class Note:
    def __init__(self, x, y, width=40, height=20, velocity=100, **kwargs):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.velocity = velocity
        self.id = None
        self.resize_id = None

        self.last_x = x
        self.last_y = y
        self.offset_x = 0
        self.offset_y = 0

class PianoRollCanvas(tk.Canvas):
    def __init__(self, master, width=800, height=400, **kwargs):
        super().__init__(master, width=width, height=height)

        self.len = kwargs.get("len",4)

        # Initialize all required attributes
        self.width = width
        self.height = height
        self.notes = []
        self.dragging = False
        self.resizing = False
        self.current_note = None
        self.last_x = 0
        self.last_y = 0

        # Grid settings
        self.grid_size = 50
        self.snap_horizontal = True
        self.snap_vertical = True

        # Bind all necessary events
        self.bind('<Button-1>', self.handle_left_click)
        self.bind('<B1-Motion>', self.handle_mouse_motion)
        self.bind('<ButtonRelease-1>', self.handle_left_release)

        # Drawing settings
        self.note_color = '#4488ff'
        self.resize_handle_color = 'red'

    def draw_background(self):
        self.delete("all")

        # Draw grid lines
        for x in range(0, self.width, self.grid_size):
            self.create_line(x, 0, x, self.height,
                             fill='#f0f0f0' if self.snap_horizontal else '#ffffff')
        for y in range(0, self.height, self.grid_size):
            self.create_line(0, y, self.width, y,
                             fill='#f0f0f0' if self.snap_vertical else '#ffffff')

        # Draw notes
        for note in self.notes:
            self._draw_note(note)

    def _snap_position(self, pos, axis='both'):
        if axis == 'horizontal' and self.snap_horizontal:
            return round(pos / self.grid_size) * self.grid_size
        elif axis == 'vertical' and self.snap_vertical:
            return round(pos / self.grid_size) * self.grid_size
        return pos

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
        item = self.find_withtag("current")
        if item:
            for note in self.notes:
                if note.id in item or note.resize_id in item:
                    self.current_note = note
                    self.current_note.offset_x = event.x-self.current_note.x
                    self.current_note.offset_y = event.y-self.current_note.y
                    if note.resize_id in item:
                        self.resizing = True
                    else:
                        self.dragging = True
                    break
            return

        # Create new note with snapped position
        x = self._snap_position(event.x, 'horizontal')
        y = self._snap_position(event.y, 'vertical')
        self.current_note = Note(x, y)
        self.notes.append(self.current_note)
        self.dragging = True

        self.draw_background()
        self.last_x = event.x
        self.last_y = event.y

    def handle_mouse_motion(self, event):
        if not self.current_note:
            return

        if self.dragging:
            dx = event.x - self.current_note.last_x ###########
            dy = event.y - self.current_note.last_y

            # Apply snap if enabled
            if self.snap_horizontal:
                self.current_note.x += self._snap_position(dx, 'horizontal') - dx
            else:
                self.current_note.x += dx - self.current_note.offset_x
                self.current_note.last_x = event.x - self.current_note.offset_x
            if self.snap_vertical:
                self.current_note.y += self._snap_position(dy, 'vertical') - dy
            else:
                self.current_note.y += dy - self.current_note.offset_y
                self.current_note.last_y = event.y - self.current_note.offset_y
        self.draw_background()

    def handle_left_release(self, event):
        self.dragging = False
        self.resizing = False
        self.current_note = None

class PianoRollEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Grid Snapping Piano Roll Editor")

        # Create main frame
        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create piano roll canvas
        self.canvas = PianoRollCanvas(self.frame)
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create control buttons
        self.create_controls()

        # Setup UI
        self.setup_ui()

    def create_controls(self):
        controls_frame = ttk.Frame(self.frame)
        controls_frame.grid(row=1, column=0, pady=5)

        # Horizontal grid toggle
        self.h_snap_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            controls_frame,
            text="Horizontal Snap",
            variable=self.h_snap_var,
            command=lambda: self.update_grid_snapping('horizontal')
        ).pack(side=tk.LEFT, padx=5)

        # Vertical grid toggle
        self.v_snap_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            controls_frame,
            text="Vertical Snap",
            variable=self.v_snap_var,
            command=lambda: self.update_grid_snapping('vertical')
        ).pack(side=tk.LEFT, padx=5)

    def update_grid_snapping(self, axis):
        if axis == 'horizontal':
            self.canvas.snap_horizontal = self.h_snap_var.get()
        else:
            self.canvas.snap_vertical = self.v_snap_var.get()
        self.canvas.draw_background()

    def setup_ui(self):
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.canvas.draw_background()

    def run(self):
        self.root.mainloop()

# Create and run the editor
editor = PianoRollEditor()
editor.run()