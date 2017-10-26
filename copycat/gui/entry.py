
import tkinter as tk
import tkinter.ttk as ttk

from .gridframe import GridFrame

class Entry(GridFrame):
    def __init__(self, parent, *args, **kwargs):
        GridFrame.__init__(self, parent, *args, **kwargs)
        self.aLabel = ttk.Label(self, text='Initial:')
        self.a      = ttk.Entry(self, style='EntryStyle.TEntry')

        self.add(self.aLabel, 0, 0)
        self.add(self.a, 0, 1)

        self.bLabel = ttk.Label(self, text='Final:')
        self.b      = ttk.Entry(self, style='EntryStyle.TEntry')

        self.add(self.bLabel, 1, 0)
        self.add(self.b, 1, 1)

        self.cLabel = ttk.Label(self, text='Next:')
        self.c      = ttk.Entry(self, style='EntryStyle.TEntry')

        self.add(self.cLabel, 2, 0)
        self.add(self.c, 2, 1)
