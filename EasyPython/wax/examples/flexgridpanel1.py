# flexgridpanel1.py
# Based on the wxPython demo.  (Sizers -> makeGrid3)

from wax import *

class MainFrame(Frame):

    def Body(self):
        p = FlexGridPanel(self, rows=3, cols=3, hgap=2, vgap=2)
        p.AddComponent(0, 0, Button(p, 'one'), expand=1)
        p.AddComponent(1, 0, Button(p, 'two'), expand=1)
        p.AddComponent(2, 0, Button(p, 'three'), expand=1)
        p.AddComponent(0, 1, Button(p, 'four'), expand=1)
        p.AddComponent(2, 1, Button(p, 'six'), expand=1)
        p.AddComponent(0, 2, Button(p, 'seven'), expand=1)
        p.AddComponent(1, 2, Button(p, 'eight'), expand=1)
        p.AddComponent(2, 2, Button(p, 'nine'), expand=1)
        p.Pack()

        p.AddGrowableRow(0)
        p.AddGrowableRow(2)
        p.AddGrowableCol(1)

        self.AddComponent(p, expand='both')
        self.Pack()

app = Application(MainFrame, direction='v')
app.Run()
