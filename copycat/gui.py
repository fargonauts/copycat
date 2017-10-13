#!/usr/bin/env python3

import sys
import time

import tkinter as tk
import tkinter.ttk as ttk

from tkinter import scrolledtext
from tkinter import filedialog

font1Size = 32
font2Size = 16
font1 = ('Helvetica', str(font1Size)) 
font2 = ('Helvetica', str(font2Size))

def create_main_canvas(root, initial, final, new, guess):
    padding  = 100

    canvas = tk.Canvas(root, borderwidth=5, relief=tk.GROOVE, background='#70747a')

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

class MainApplication(ttk.Frame):
    MAX_COLUMNS = 10

    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.widgets = dict()

        self.parent = parent
        self.create_widgets()
        self.canvas = None
        self.columnconfigure(0)
        self.rowconfigure(0)

    def create_widgets(self):
        self.canvas = create_main_canvas(self, 'abc', 'abd', 'ijk', '')
        self.canvas.grid(column=0, row=0, sticky=tk.N+tk.S+tk.E+tk.W)

        temp_label = ttk.Label(self, text='', background='#70747a', foreground='white', borderwidth=5, relief=tk.GROOVE, font=font2, padding=30)
        temp_label.grid(column=1, row=0, sticky=tk.N+tk.S+tk.E+tk.W)
        self.widgets['temp'] = temp_label

    def update_slipnodes(self):
        self.canvas = create_main_canvas(self.root, 'abc', 'abd', 'ijk', '')

class GUI(object):
    def __init__(self, title):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry('1200x800')
        self.app = MainApplication(self.root)
        self.app.pack(side='top', fill='both', expand=True)

    def update(self, temp, slipnodes):
        self.root.update_idletasks()
        self.root.update()
        self.app.widgets['temp']['text'] = 'Temp:\n{}'.format(round(temp, 2))
        self.app.update()
