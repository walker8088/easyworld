# panels-1.py
# Demonstrate border styles for Panel.

from wax import *

STYLES = ('simple', 'double', 'sunken', 'raised', 'static', 'none')

class MainFrame(VerticalFrame):
    def Body(self):
        gp = FlexGridPanel(self, rows=len(STYLES), cols=2, hgap=2, vgap=2,
             growable_cols=[1])
        for index in range(len(STYLES)):
            borderstyle = STYLES[index]
            p = Panel(gp, border=borderstyle)
            p.Size = (300, 50)
            gp.AddComponent(1, index, p, border=3, expand=1)
            # XXX FlexGridPanel doesn't support 'expand strings' (yet?)
            label = Label(gp, borderstyle)
            gp.AddComponent(0, index, label, border=3, expand=0, align='c')
            label.BackgroundColor = p.BackgroundColor
        self.BackgroundColor = p.BackgroundColor
        gp.Pack()

        self.AddComponent(gp, expand="both", border=4)
        self.Pack()


app = Application(MainFrame)
app.Run()



