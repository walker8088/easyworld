# simplebuttons4.py
# Button with a border...

import sys
sys.path.append("../..")

from wax import *

WaxConfig.default_font = ("Verdana", 9)

class MainFrame(Frame):
    def Body(self):
        b = Button(self, "one")
        b.SetSize((80, 80))
        self.AddComponent(b, expand='both', border=15)
        self.Pack()

app = Application(MainFrame)
app.MainLoop()
