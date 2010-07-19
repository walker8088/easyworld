# gridpanel3.py

from wax import *

class MainFrame(Frame):

    def Body(self):
        p3 = GridPanel(self, rows=3, cols=3)

        p = Panel(p3, direction='v')
        p.AddComponent(Button(p, "A"), expand='h')
        p.AddComponent(Button(p, "B"), expand='both')
        p.Pack()

        p2 = GridPanel(p3, rows=2, cols=2, hgap=4, vgap=4)
        p2.AddComponent(0, 0, Button(p2, "C"), expand=1)
        p2.AddComponent(1, 0, Button(p2, "E"), expand=1)
        p2.AddComponent(0, 1, Button(p2, "F"), expand=1)
        p2.AddComponent(1, 1, Button(p2, "G"), expand=1)
        p2.Pack()

        p3.AddComponent(0, 0, Button(p3, 'one'), expand=0, align='rb')
        p3.AddComponent(1, 0, Button(p3, 'two'), expand=1)
        p3.AddComponent(2, 0, Button(p3, 'three'), expand=0, align='lb')
        p3.AddComponent(0, 1, Button(p3, 'four'), expand=1)
        p3.AddComponent(1, 1, Button(p3, 'five'), expand=0, align='c')
        p3.AddComponent(2, 1, Button(p3, 'six'), expand=1)
        p3.AddComponent(0, 2, p, expand=1, border=10)
        p3.AddComponent(1, 2, Button(p3, 'eight'), expand=1)
        p3.AddComponent(2, 2, p2, expand=1, border=4)
        p3.Pack()
        p3.SetSize((400, 200))

        self.AddComponent(p3, expand='both')

        statusbar = StatusBar(self)
        self.SetStatusBar(statusbar)
        statusbar[0] = "Resize this window to see how the sizers respond..."

        self.Pack()
        self.SetSize((300, 300))

if __name__ == "__main__":

    app = Application(MainFrame, title='GridPanel demo', direction='v')
    app.Run()

