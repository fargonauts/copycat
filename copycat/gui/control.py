import tkinter as tk
import tkinter.ttk as ttk

class Control(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.paused = True

        #self.style = ttk.Style()
        #self.style.configure('TButton', background='black', foreground='white')

        #self.playbutton = ttk.Button(self, text='Play/Pause', command=lambda : self.play())
        self.playbutton = tk.Button(self, text='Play', command=lambda : self.toggle(), background='black', foreground='white', activebackground='black', activeforeground='blue')
        self.playbutton.grid(column=0, row=0, stick=tk.N+tk.E+tk.S+tk.W)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def toggle(self):
        self.paused = not self.paused
        self.playbutton['text'] = 'Pause' if not self.paused else 'Play'
    #def step(self):
