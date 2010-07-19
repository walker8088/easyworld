# togglebutton1.py

import sys
sys.path.append("../..")

from wax import *

WaxConfig.default_font = ("Verdana", 9)

class MainFrame(Frame):
    def Body(self):
        callback = self.OnButtonClick
        self.AddComponent(ToggleButton(self, "one", event=callback), expand='v')
        self.AddComponent(ToggleButton(self, "two", event=callback), expand='h')
        self.AddComponent(ToggleButton(self, "three", event=callback))
        self.Pack()
    def OnButtonClick(self, event=None):
        b = event.GetEventObject()
        print "Button", repr(b.GetLabel()), "is",
        print b.Pressed() and "pressed" or "not pressed"

app = Application(MainFrame)
app.MainLoop()
