import tkinter as tk
import tkinter.ttk as ttk

class GridFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

    def add(self, element, x, y, xspan=1, yspan=1):
        element.grid(column=x, row=y, columnspan=xspan, rowspan=yspan, sticky=tk.N+tk.E+tk.S+tk.W)
        tk.Grid.rowconfigure(self, x, weight=1)
        tk.Grid.columnconfigure(self, y, weight=1)
