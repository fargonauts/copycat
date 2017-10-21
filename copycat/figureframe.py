import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import tkinter as tk
import tkinter.ttk as ttk

import time

LARGE_FONT = ('Verdana', 14)

class FigureFrame(tk.Frame):

    def __init__(self, parent, figure, title):
        self.figure = figure

        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text=title, font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def update(self, figure):
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.show()

if __name__ == '__main__':
    root = tk.Tk()

    x = [1,2,3,4]
    y = [2,3,4,5]
    f = Figure(figsize=(5,5), dpi=100)
    a = f.add_subplot(111)
    a.plot(x, y)

    figure = FigureFrame(root, f, 'Lines')
    figure.pack()

    i = 0
    while True:
        root.update()
        root.update_idletasks()
        time.sleep(1)
        i += 1
        x += [i]
        y += [i**2]
        print(x, y)
        f = Figure(figsize=(5,5), dpi=100)
        a = f.add_subplot(111)
        a.plot(x, y)
        #a.clear()
        #a.plot(x, y)
        figure = FigureFrame(root, f, 'Lines')
