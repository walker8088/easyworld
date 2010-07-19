# setcursor-1.py
# Demonstrates window.SetCursor() and MousePointers object.

from wax import *

class MainFrame(VerticalFrame):

    def Body(self):
        label = Label(self, "Choose a pointer:")
        self.AddComponent(label, border=3)
        # register custom cursor
        MousePointers.RegisterImage('trident', 'heretic2.ico')
        cb1 = ComboBox(self, MousePointers.GetNames(), readonly=1, sort=1)
        cb1.OnSelect = self.OnCb1Select
        self.AddComponent(cb1, expand='h', border=3)
        self.panel = Panel(self, size=(100,100), border='simple')

        self.AddComponent(self.panel, expand='both', border=3)

        self.Pack()

        self.BackgroundColor = label.BackgroundColor = 'white'
        self.cb1 = cb1
        self.Size = 150,150

    def OnCb1Select(self, event):
        self.panel.SetCursor(self.cb1.Value)

app = Application(MainFrame, resize=0)
app.Run()
