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

        self.playbutton = ttk.Button(self, text='Play', command=lambda : self.toggle())
        self.add(self.playbutton, 0, 0)

        self.stepbutton = ttk.Button(self, text='Step', command=lambda : self.step())
        self.add(self.stepbutton, 1, 0)

        self.entry = Entry(self)
        self.add(self.entry, 0, 1, xspan=2)

        self.gobutton = ttk.Button(self, text='Go', command=lambda : self.set_go())
        self.add(self.gobutton, 0, 2, xspan=2)

    def play(self):
        self.paused = False
        self.playbutton['text'] = 'Pause'

    def pause(self):
        self.paused = True
        self.playbutton['text'] = 'Play'

    def toggle(self):
        if self.paused:
            self.play()
        else:
            self.pause()

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
        self.play()

    def get_vars(self):
        return self.entry.a.get(), self.entry.b.get(), self.entry.c.get()
