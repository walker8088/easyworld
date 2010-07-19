# events-1.py

from wax import *

NUM_BUTTONS = 5

def OnEnter(event):
    obj = event.GetEventObject()
    obj.SetForegroundColor('blue')

def OnLeave(event):
    obj = event.GetEventObject()
    obj.SetForegroundColor('black')

class MainFrame(Frame):
    def Body(self):
        # when you move the mouse cursor over a button, its text turns blue.
        # BUG?: apparently when you leave the window, OnLeave isn't called
        # for the button you were last in.
        for i in range(NUM_BUTTONS):
            b = Button(self, "Button " + str(i+1))
            b.OnEnter = OnEnter
            b.OnLeave = OnLeave
            self.AddComponent(b, stretch=1)
        self.Pack()

app = Application(MainFrame, direction='v')
app.Run()
