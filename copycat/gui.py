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

style = dict(background='black', 
             foreground='white',  
             borderwidth=5, 
             relief=tk.GROOVE, 
             font=font2)

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
        self.canvas = create_main_canvas(self, 'abc', 'abd', 'ijk', '?')
        self.canvas.grid(column=0, row=0, sticky=tk.N+tk.S+tk.E+tk.W)

        tempLabel = ttk.Label(self, text='', **style, padding=30)
        tempLabel.grid(column=1, row=0, sticky=tk.N+tk.S+tk.E+tk.W)
        self.widgets['temp'] = tempLabel

        slipList = tk.Listbox(self, **style)
        slipList.grid(column=2, row=0, sticky=tk.N+tk.S+tk.E+tk.W)
        self.widgets['sliplist'] = slipList

        codeletList = tk.Listbox(self, **style)
        codeletList.grid(column=3, row=0, sticky=tk.N+tk.S+tk.E+tk.W)
        self.widgets['codeletlist'] = codeletList

    def update(self, copycat):
        temp      = copycat.temperature.value()
        slipnodes = copycat.slipnet.slipnodes
        codelets  = copycat.coderack.codelets
        answer    = '' if copycat.workspace.rule is None else copycat.workspace.rule.buildTranslatedRule()

        slipList = self.widgets['sliplist']
        slipList.delete(0, slipList.size())

        self.canvas = create_main_canvas(self, 'abc', 'abd', 'ijk', answer)
        self.canvas.grid(column=0, row=0, sticky=tk.N+tk.S+tk.E+tk.W)
        self.widgets['temp']['text'] = 'Temp:\n{}'.format(round(temp, 2))
        slipnodes = sorted(slipnodes, key=lambda s:s.activation, reverse=True)
        for item in slipnodes:
            listStr = '{}: {}'.format(item.name, round(item.activation, 2))
            slipList.insert(tk.END, listStr)

        codeletList = self.widgets['codeletlist']
        codeletList.delete(0, codeletList.size())
        codelets = sorted(codelets, key=lambda c:c.urgency, reverse=True)
        for codelet in codelets:
            listStr = '{}: {}'.format(codelet.name, round(codelet.urgency, 2))
            codeletList.insert(tk.END, listStr)

        descriptionsFrame = tk.Frame(self)
        for i, obj in enumerate(sorted(copycat.workspace.objects, key=lambda o:o.string.string)):
            l = tk.Label(descriptionsFrame, text=obj.string.string)
            l.grid(column=i, row=0)
            for j, description in enumerate(obj.descriptions):
                l = tk.Label(descriptionsFrame, text='[]')
                l.grid(column=i, row=j+1)
        descriptionsFrame.grid(row=1)


class GUI(object):
    def __init__(self, title, updateInterval=.1):
        self.root = tk.Tk()
        self.root.title(title)
        #self.root.geometry('1200x800')
        self.app = MainApplication(self.root)
        self.app.pack(fill=tk.Y)

        self.lastUpdated = time.time()
        self.updateInterval = updateInterval

    def update(self, copycat):
        self.root.update_idletasks()
        self.root.update()
        current = time.time()
        if current - self.lastUpdated > self.updateInterval:
            self.app.update(copycat)
            self.lastUpdated = current
