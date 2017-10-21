import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import tkinter as tk
import tkinter.ttk as ttk

import time
import matplotlib.animation as animation

import matplotlib.pyplot as plt

LARGE_FONT = ('Verdana', 20)

plt.style.use('dark_background')

class StatusFrame(ttk.Frame):
    def __init__(self, parent, status, title, toolbar=False):
        ttk.Frame.__init__(self, parent)
        self.status = status

        self.canvas = FigureCanvasTkAgg(status.figure, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.animation = animation.FuncAnimation(status.figure, lambda i : status.update_plots(i), interval=1000)

        if toolbar:
            toolbar = NavigationToolbar2TkAgg(self.canvas, self)
            toolbar.update()
            self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class Status(object):
    def __init__(self):
        self.figure  = Figure(figsize=(5,5), dpi=100)
        self.subplot = self.figure.add_subplot(111)
        self.x       = []
        self.y       = []
        self.update_plots(0)

    def update_plots(self, i):
        self.subplot.clear()
        with plt.style.context(('dark_background')):
            self.subplot.plot(self.x, self.y)

if __name__ == '__main__':
    app = tk.Tk()
    status = Status()
    sframe = StatusFrame(app, status, 'x**2')
    sframe.pack()

    i = 0
    while True:
        app.update()
        app.update_idletasks()
        time.sleep(.01)
        i += 1
        status.x += [i]
        status.y += [i**2]
