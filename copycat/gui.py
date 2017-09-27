#!/usr/bin/env python3

import sys
import time

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import scrolledtext
from tkinter import filedialog



class MainApplication(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.widgets = dict()
        self.parent = parent
        self.create_widgets()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def create_widgets(self):
        """Contains all widgets in main application."""

        main_label = tk.Label(self, text="abc:abd::ijk:?", background='black', foreground='white')
        main_label.grid(column=0, row=0, columnspan=9, rowspan=4)
        self.widgets['main'] = main_label
        temp_label = tk.Label(self, text='temp')
        temp_label.grid(column=9, row=0, rowspan=1, sticky=tk.E)
        self.widgets['temp'] = temp_label

        example_net = [
                ('left', 100),
                ('right', 100),
                ('a', 10),
                ('b', 9),
                ('rightmost', 100)
                ]

        MAX_COLUMNS = 10
        MAX_ROWS    = 4

        row = 0
        for i, (name, amount) in enumerate(example_net):
            column = i % MAX_COLUMNS
            if column == 0:
                row += 1
            if row + 1 >= MAX_ROWS:
                break
            l = tk.Label(self, text='{}\n({})'.format(name, amount))
            l.grid(column=column, row=row, sticky=tk.SE)
            self.widgets[str(column) + ',' + str(row)] = l

class GUI(object):
    def __init__(self, title):
        self.root = tk.Tk()
        self.root.title(title)
        self.app = MainApplication(self.root)
        self.app.pack(side='top', fill='both', expand=True)

    def update(self, temp, slipnodes):
        self.root.update_idletasks()
        self.root.update()
        self.app.widgets['temp']['text'] = 'Temp:({})'.format(temp)
        print(slipnodes)
        time.sleep(.01)
