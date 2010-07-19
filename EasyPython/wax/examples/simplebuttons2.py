# simplebuttons2.py

import sys
sys.path.append("../..")

from wax import *

WaxConfig.default_font = ("Verdana", 9)

class MainFrame(Frame):
    def Body(self):
        self.AddComponent(Button(self, "one"), expand='h', align="top")
        self.AddComponent(Button(self, "two"), expand='both')
        self.AddComponent(Button(self, "three"), expand='h', align="center")
        self.AddComponent(Button(self, "four"), expand='both')
        self.AddComponent(Button(self, "five"), expand='h', align="bottom")
        self.Pack()

app = Application(MainFrame)
app.MainLoop()
