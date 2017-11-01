import tkinter as tk
import tkinter.ttk as ttk

from tkinter import scrolledtext
from tkinter import filedialog

from .control import Control
from .gridframe import GridFrame

from .workspacecanvas import WorkspaceCanvas

class Primary(GridFrame):

    def __init__(self, parent, *args, **kwargs):
        GridFrame.__init__(self, parent, *args, **kwargs)

        self.canvas = WorkspaceCanvas(self)
        self.add(self.canvas, 0, 0, xspan=2)

        self.control = Control(self)
        self.add(self.control, 0, 2)

        GridFrame.configure(self)

    def update(self, copycat):
        self.canvas.update(copycat)

    def reset_with_strings(self, initial, modified, target):
        self.canvas.reset_with_strings(initial, modified, target)
