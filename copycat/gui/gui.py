import sys
import time

import tkinter as tk
import tkinter.ttk as ttk

from tkinter import scrolledtext
from tkinter import filedialog

import matplotlib.pyplot as plt

from .status import Status, StatusFrame
from .gridframe import GridFrame
from .primary import Primary

from .plot import plot_imbedded

font1Size = 32
font2Size = 12
font1 = ('Helvetica', str(font1Size)) 
font2 = ('Helvetica', str(font2Size))

style = dict(background='black', 
             foreground='white',  
             font=font2)

plt.style.use('dark_background')

class MainApplication(GridFrame):

    def __init__(self, parent, *args, **kwargs):
        GridFrame.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.primary = Primary(self, *args, **kwargs)
        self.add(self.primary, 0, 0)
        self.create_widgets()
        
        self.iterations = 0

        self.messages = []

    def log(self, message):
        self.messages.append(message)

    def create_widgets(self):

        self.slipList = tk.Listbox(self, **style, bd=0)
        self.add(self.slipList, 0, 1)

        self.codeletList = tk.Listbox(self, **style, bd=0)
        self.add(self.codeletList, 1, 1)

        self.objectList = tk.Listbox(self, **style, bd=0)
        self.add(self.objectList, 2, 1)

        self.logBox = tk.Label(self, text='', **style, bd=1)
        self.add(self.logBox, 1, 0)
        self.graph2 = Status()
        sframe2 = StatusFrame(self, self.graph2, 'graph 2')
        self.add(sframe2, 2, 0)

    def update(self, copycat):
        self.iterations += 1
        self.primary.update(copycat)

        slipnodes = copycat.slipnet.slipnodes
        codelets  = copycat.coderack.codelets
        objects   = copycat.workspace.objects

        self.slipList.delete(0, self.slipList.size())
        slipnodes = sorted(slipnodes, key=lambda s:s.activation, reverse=True)
        for item in slipnodes:
            listStr = '{}: {}'.format(item.name, round(item.activation, 2))
            self.slipList.insert(tk.END, listStr)

        self.codeletList.delete(0, self.codeletList.size())
        codelets = sorted(codelets, key=lambda c:c.urgency, reverse=True)
        for codelet in codelets:
            listStr = '{}: {}'.format(codelet.name, round(codelet.urgency, 2))
            self.codeletList.insert(tk.END, listStr)

        self.objectList.delete(0, self.objectList.size())
        #objects = sorted(objects, key=lambda c:c.urgency, reverse=True)
        for o in objects:
            #listStr = '{}: {}'.format(o.name, round(o.urgency, 2))
            listStr = str(o)
            self.objectList.insert(tk.END, listStr)

        self.logBox['text'] = '\n'.join(list(reversed(self.messages))[:10])
        if len(self.messages) > 10:
            self.logBox['text'] += '\n...'

    def reset_with_strings(self, initial, modified, target):
        self.primary.reset_with_strings(initial, modified, target)

class GUI(object):
    def __init__(self, title, updateInterval=.1):
        self.root = tk.Tk()
        self.root.title(title)
        tk.Grid.rowconfigure(self.root, 0, weight=1)
        tk.Grid.columnconfigure(self.root, 0, weight=1)
        self.app = MainApplication(self.root)
        self.app.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)

        self.lastUpdated = time.time()
        self.updateInterval = updateInterval

    def add_answers(self, answers):
        def modifier(status):
            with plt.style.context(('dark_background')):
                plot_imbedded(answers, status)
        self.app.graph2.modifier = modifier 

    def refresh(self):
        self.root.update_idletasks()
        self.root.update()

    def update(self, copycat):
        current = time.time()
        if current - self.lastUpdated > self.updateInterval:
            self.app.update(copycat)
            self.lastUpdated = current
