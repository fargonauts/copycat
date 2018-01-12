import sys
import time

import tkinter as tk
import tkinter.ttk as ttk

from tkinter import scrolledtext
from tkinter import filedialog

import matplotlib.pyplot as plt

from .status import Status, StatusFrame
from .status import Plot
from .gridframe import GridFrame
from .primary import Primary
from .list import List
from .style import configure_style

from .plot import plot_answers, plot_temp

plt.style.use('dark_background')

class MainApplication(GridFrame):

    def __init__(self, parent, *args, **kwargs):
        GridFrame.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.primary = Primary(self, *args, **kwargs)
        self.add(self.primary, 0, 0, xspan=2)
        self.create_widgets()
        GridFrame.configure(self)

    def create_widgets(self):
        columns = 20
        self.slipList = List(self, columns)
        self.add(self.slipList, 0, 1)

        self.codeletList = List(self, columns)
        self.add(self.codeletList, 1, 1)

        self.objectList = List(self, columns)
        self.add(self.objectList, 2, 1, xspan=2)

        self.graph1 = Plot(self, 'Temperature history')
        self.add(self.graph1, 2, 0)

        self.graph2 = Plot(self, 'Answer Distribution')
        self.add(self.graph2, 3, 0)

    def update(self, copycat):
        self.primary.update(copycat)

        slipnodes = copycat.slipnet.slipnodes
        codelets  = copycat.coderack.codelets
        objects   = copycat.workspace.objects

        self.slipList.update(slipnodes, key=lambda s:s.activation, 
                formatter=lambda s : '{}: {}'.format(s.name, round(s.activation, 2)))
        self.codeletList.update(codelets, key=lambda c:c.urgency, formatter= lambda s : '{}: {}'.format(s.name, round(s.urgency, 2)))
        get_descriptors = lambda s : ', '.join('({}={})'.format(d.descriptionType.name, d.descriptor.name) for d in s.descriptions)
        self.objectList.update(objects, formatter=lambda s : '{}: {}'.format(s, get_descriptors(s)))
        
        def modifier(status):
            with plt.style.context(('dark_background')):
                plot_temp(copycat.temperature, status)
        self.graph1.status.modifier = modifier

    def reset_with_strings(self, initial, modified, target):
        self.primary.reset_with_strings(initial, modified, target)

class GUI(object):
    def __init__(self, title):
        self.root = tk.Tk()
        self.root.title(title)
        tk.Grid.rowconfigure(self.root, 0, weight=1)
        tk.Grid.columnconfigure(self.root, 0, weight=1)
        self.app = MainApplication(self.root)
        self.app.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        configure_style(ttk.Style())

    def add_answers(self, answers):
        def modifier(status):
            with plt.style.context(('dark_background')):
                plot_answers(answers, status)
        self.app.graph2.status.modifier = modifier 

    def refresh(self):
        self.root.update_idletasks()
        self.root.update()

    def paused(self):
        return self.app.primary.control.paused

    def update(self, copycat):
        self.app.update(copycat)
