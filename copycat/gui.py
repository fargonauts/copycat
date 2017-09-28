#!/usr/bin/env python3

import sys
import time

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import scrolledtext
from tkinter import filedialog

class MainApplication(ttk.Frame):
    MAX_COLUMNS = 10

    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.widgets = dict()

        self.parent = parent
        self.create_widgets()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def create_widgets(self):
        """Contains all widgets in main application."""

        main_label = ttk.Label(self, text="abc:abd::ijk:?", background='black', foreground='white')
        main_label.grid(column=0, row=0, columnspan=9, rowspan=4)
        self.widgets['main'] = main_label
        temp_label = ttk.Label(self, text='temp')
        temp_label.grid(column=9, row=0, rowspan=1, sticky=tk.E)
        self.widgets['temp'] = temp_label

    def update_slipnodes(self, slipnodes):
        slipnodes = [(node.name, round(node.activation, 2)) for node in slipnodes]
        row = 0
        for i, (name, amount) in enumerate(slipnodes):
            column = i % MainApplication.MAX_COLUMNS
            if column == 0 and i != 0:
                row += 1
            text = text='{}\n({})'.format(name, amount)
            if name not in self.widgets:
                l = ttk.Label(self, text=text)
                l.grid(column=column*2, columnspan=2, row=row+3, sticky=tk.SE)
                self.widgets[name] = l
            else:
                self.widgets[name]['text'] = text

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
        self.app.widgets['temp']['text'] = 'Temp:({})'.format(temp)
        self.app.update_slipnodes(slipnodes)
