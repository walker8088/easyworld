# event-onsize.py

from wax import *

class MainFrame(Frame):
    def OnResize(self, event):
        print "Window resized to:", self.GetSize()
        event.Skip()

app = Application(MainFrame)
app.Run()
