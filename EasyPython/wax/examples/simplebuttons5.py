# simplebuttons5.py
# Putting buttons left and right, with variable space in between them, like
# Tkinter can...

import sys
sys.path.append("../..")

from wax import *

WaxConfig.default_font = ("Verdana", 9)

class MainFrame(Frame):
    def Body(self):
        self.AddComponent(Button(self, "left"), expand='v')
        self.AddSpace(60, 20, expand='both')
        self.AddComponent(Button(self, "right"), expand='v')
        self.Pack()

app = Application(MainFrame)
app.MainLoop()
