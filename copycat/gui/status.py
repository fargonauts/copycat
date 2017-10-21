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

LARGE_FONT = ('Verdana', 20)

class StatusFrame(tk.Frame):
    def __init__(self, parent, status, title):
        self.status = status

        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text=title, font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        canvas = FigureCanvasTkAgg(status.figure, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.animation = animation.FuncAnimation(status.figure, lambda i : status.update_plots(i), interval=1000)


class Status(object):
    def __init__(self):
        self.figure  = Figure(figsize=(5,5), dpi=100)
        self.subplot = self.figure.add_subplot(111)
        self.x       = []
        self.y       = []

    def update_plots(self, i):
        self.subplot.clear()
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
