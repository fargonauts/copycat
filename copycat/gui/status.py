import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import tkinter as tk
import tkinter.ttk as ttk

import time
import matplotlib.animation as animation

import matplotlib.pyplot as plt

plt.style.use('dark_background')

from .gridframe import GridFrame

class Plot(GridFrame):
    def __init__(self, parent, title):
        GridFrame.__init__(self, parent)
        self.status = Status()
        self.sframe = StatusFrame(self, self.status, title)
        self.add(self.sframe, 0, 0, xspan=2)

        self.savebutton = ttk.Button(self, text='Save to path:', command=lambda : self.save())
        self.add(self.savebutton, 0, 1)

        self.pathentry = ttk.Entry(self, style='EntryStyle.TEntry', textvariable='output/dist.png')
        self.add(self.pathentry, 1, 1)

    def save(self):
        path = self.pathentry.get()
        if len(path) > 0:
            try:
                self.status.figure.savefig(path)
            except Exception as e:
                print(e)

class StatusFrame(ttk.Frame):
    def __init__(self, parent, status, title):
        ttk.Frame.__init__(self, parent)
        self.status = status

        self.canvas = FigureCanvasTkAgg(status.figure, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.animation = animation.FuncAnimation(status.figure, lambda i : status.update_plots(i), interval=1000)

class Status(object):
    def __init__(self):
        self.figure  = Figure(figsize=(5,5), dpi=100)
        self.subplot = self.figure.add_subplot(111)
        self.x       = []
        self.y       = []

        def modifier(status):
            with plt.style.context(('dark_background')):
                status.subplot.plot(status.x, status.y)

        self.modifier = modifier
        self.update_plots(0)

    def update_plots(self, i):
        self.subplot.clear()
        self.modifier(self)
