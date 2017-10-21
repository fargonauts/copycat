import tkinter as tk
import tkinter.ttk as ttk

from .gridframe import GridFrame

class Control(GridFrame):
    def __init__(self, parent, *args, **kwargs):
        GridFrame.__init__(self, parent, *args, **kwargs)

        self.paused = True
        self.steps  = 0

        self.playbutton = tk.Button(self, text='Play', command=lambda : self.toggle(), background='black', foreground='white', activebackground='black', activeforeground='blue')
        self.add(self.playbutton, 0, 0)

        self.stepbutton= tk.Button(self, text='Step', command=lambda : self.step(), background='black', foreground='white', activebackground='black', activeforeground='blue')
        self.add(self.stepbutton, 1, 0)

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
