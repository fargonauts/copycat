import tkinter as tk
import tkinter.ttk as ttk

from .gridframe import GridFrame

font1Size = 16
font1 = ('Helvetica', font1Size)

class WorkspaceCanvas(GridFrame):

    def __init__(self, parent, *args, **kwargs):
        GridFrame.__init__(self, parent, *args, **kwargs)

        self.initial  = ''
        self.modified = ''
        self.target   = ''
        self.answer   = ''

        self.changed  = False

        self.canvas = tk.Canvas(self, background='black')
        self.add(self.canvas, 0, 0)
        GridFrame.configure(self)

    def update(self, copycat):
        answer = '' if copycat.workspace.rule is None else copycat.workspace.rule.buildTranslatedRule()
        if answer != self.answer:
            self.changed = True

        if self.changed:
            self.canvas.delete('all')
            self.add_text()

    def add_text(self):
        padding = 100

        def add_sequences(sequences, x, y):
            for sequence in sequences:
                x += padding
                if sequence is None:
                    sequence = ''
                for char in sequence:
                    self.canvas.create_text(x, y, text=char, anchor=tk.NW, font=font1, fill='white')
                    x += font1Size
            return x, y

        x = 0
        y = padding

        add_sequences([self.initial, self.modified], x, y)

        x = 0
        y += padding

        add_sequences([self.target, self.answer], x, y)

    def reset_with_strings(self, initial, modified, target):
        if initial != self.initial or \
           modified != self.modified or \
           target != self.target:
            self.changed = True
        self.initial  = initial
        self.modified = modified
        self.target   = target
