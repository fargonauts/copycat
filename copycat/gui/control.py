import tkinter as tk
import tkinter.ttk as ttk

from .gridframe import GridFrame
from .entry     import Entry

class Control(GridFrame):
    def __init__(self, parent, *args, **kwargs):
        GridFrame.__init__(self, parent, *args, **kwargs)

        self.paused = True
        self.steps  = 0
        self.go     = False

        self.playbutton = tk.Button(self, bd=0, text='Play', command=lambda : self.toggle(), background='black', foreground='white', activebackground='black', activeforeground='blue')
        self.add(self.playbutton, 0, 0)

        self.stepbutton = tk.Button(self, bd=0, text='Step', command=lambda : self.step(), background='black', foreground='white', activebackground='black', activeforeground='blue')
        self.add(self.stepbutton, 1, 0)

        self.entry = Entry(self)
        self.add(self.entry, 0, 1, xspan=2)

        self.gobutton = tk.Button(self, bd=0, text='Go', command=lambda : self.set_go(), background='black', foreground='white', activebackground='black', activeforeground='blue')
        self.add(self.gobutton, 0, 2, xspan=2)

    def toggle(self):
        self.paused = not self.paused
        self.playbutton['text'] = 'Pause' if not self.paused else 'Play'

    def step(self):
        self.steps += 1

    def has_step(self):
        if self.steps > 0:
            self.steps -= 1
            return True
        else:
            return False

    def set_go(self):
        self.go = True

    def get_vars(self):
        return self.entry.a.get(), self.entry.b.get(), self.entry.c.get()
