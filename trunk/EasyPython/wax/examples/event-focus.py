# event-focus.py

from wax import *

class MainFrame(Frame):
    def Body(self):
        textboxen = []
        for i in range(10):
            text = TextBox(self)
            text.OnGetFocus = self.OnTextBoxGetFocus
            text.OnLoseFocus = self.OnTextBoxLoseFocus
            self.AddComponent(text, expand=1, border=2)
        self.Pack()
    def OnTextBoxGetFocus(self, event):
        print "Control", event.GetEventObject(), "gets focus!"
    def OnTextBoxLoseFocus(self, event):
        print "Control", event.GetEventObject(), "loses focus!"

app = Application(MainFrame, direction='v', tab_traversal=1)
# you can walk through the screen using Tab
app.Run()
