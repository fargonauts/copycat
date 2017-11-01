import tkinter as tk
import tkinter.ttk as ttk

import time

from .gridframe import GridFrame

class List(GridFrame):

    def __init__(self, parent, columns, updateInterval=.1):
        GridFrame.__init__(self, parent)
        self.text = ttk.Label(self, anchor='w', justify=tk.LEFT, width=30)
        self.add(self.text, 0, 0)

        self.columns = columns

        self.lastUpdated = time.time()
        self.updateInterval = updateInterval

    def update(self, l, key=None, reverse=False, formatter=lambda s : str(s)):
        current = time.time()
        if current - self.lastUpdated > self.updateInterval:
            l = l[:self.columns]
            if key is not None:
                l = sorted(l, key=key, reverse=False)
            self.text['text'] = '\n'.join(map(formatter, l))
