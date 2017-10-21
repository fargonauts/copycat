import tkinter as tk
import tkinter.ttk as ttk

from tkinter import scrolledtext
from tkinter import filedialog

from .control import Control

font1Size = 32
font2Size = 16
font1 = ('Helvetica', str(font1Size)) 
font2 = ('Helvetica', str(font2Size))

style = dict(background='black', 
             foreground='white',  
             font=font2)

def create_main_canvas(root, initial, final, new, guess):
    padding  = 100

    canvas = tk.Canvas(root, background='black')

    def add_sequences(sequences, x, y):
        for sequence in sequences:
            x += padding
            for char in sequence:
                canvas.create_text(x, y, text=char, anchor=tk.NW, font=font1, fill='white')
                x += font1Size
        return x, y

    x = 0
    y = padding

    add_sequences([initial, final], x, y)

    x = 0
    y += padding

    add_sequences([new, guess], x, y)

    canvas['height'] = str(int(canvas['height']) + padding)
    canvas['width']  = str(int(canvas['width'])  + padding)

    return canvas

class Primary(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        self.canvas = create_main_canvas(self, 'abc', 'abd', 'ijk', '?')
        self.canvas.grid(column=0, row=0, rowspan=2, sticky=tk.N+tk.S+tk.E+tk.W)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.control = Control(self)
        self.control.grid(column=0, row=2, sticky=tk.N+tk.S+tk.E+tk.W)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)

    def update(self, copycat):
        answer    = '' if copycat.workspace.rule is None else copycat.workspace.rule.buildTranslatedRule()
        self.canvas = create_main_canvas(self, 'abc', 'abd', 'ijk', answer)
        self.canvas.grid(column=0, row=0, rowspan=2, sticky=tk.N+tk.S+tk.E+tk.W)
