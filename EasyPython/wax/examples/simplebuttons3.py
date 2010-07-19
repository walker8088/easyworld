# simplebuttons3.py
# Add a spacer...

import sys
sys.path.append("../..")

from wax import *

WaxConfig.default_font = ("Verdana", 9)

class MainFrame(Frame):
    def Body(self):
        self.AddComponent(Button(self, "one"), expand='v')
        self.AddComponent(Button(self, "two"), expand='both')
        self.AddSpace(60, 20, expand='v')
        self.AddComponent(Button(self, "three"), expand='v')
        self.Pack()

app = Application(MainFrame)
app.MainLoop()
