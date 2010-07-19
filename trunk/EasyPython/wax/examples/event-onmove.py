# event-onmove.py

from wax import *

class MainFrame(Frame):
    def OnMove(self, event):
        print "Window moved to:", self.GetPosition()
        event.Skip()

app = Application(MainFrame)
app.Run()
