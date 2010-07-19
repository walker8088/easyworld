# simplebuttons.py

import sys
sys.path.append("../..")

from wax import *

WaxConfig.default_font = ("Verdana", 9)

class MainFrame(Frame):
    def Body(self):
        self.AddComponent(Button(self, "one"), expand='v')
        self.AddComponent(Button(self, "two"), expand='h')
        self.AddComponent(Button(self, "three"))
        self.Pack()

app = Application(MainFrame)
app.MainLoop()
