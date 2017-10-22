
import tkinter as tk
import tkinter.ttk as ttk

from .gridframe import GridFrame

style = dict(background='black', foreground='white')

class Entry(GridFrame):
    def __init__(self, parent, *args, **kwargs):
        GridFrame.__init__(self, parent, *args, **kwargs)
        self.aLabel = tk.Label(self, text='Initial:', **style)
        self.a      = tk.Entry(self, **style)

        self.add(self.aLabel, 0, 0)
        self.add(self.a, 0, 1)

        self.bLabel = tk.Label(self, text='Final:', **style)
        self.b      = tk.Entry(self, **style)

        self.add(self.bLabel, 1, 0)
        self.add(self.b, 1, 1)

        self.cLabel = tk.Label(self, text='Next:', **style)
        self.c      = tk.Entry(self, **style)

        self.add(self.cLabel, 2, 0)
        self.add(self.c, 2, 1)
