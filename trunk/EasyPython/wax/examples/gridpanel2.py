# gridpanel2.py

from wax import *

class MainFrame(Frame):
    def Body(self):
        gp = GridPanel(self, rows=2, cols=3, hgap=1, vgap=1)
        assert gp.sizer.GetRows() == 2
        assert gp.sizer.GetCols() == 3
        print gp.controls.keys()
        gp.AddComponent(0, 0, Button(gp, '(0,0)'), expand=1, border=5)
        gp.AddComponent(0, 1, Button(gp, '(0,1)'), expand=1)
        gp.AddComponent(1, 0, Button(gp, '(1,0)'), expand=1)
        gp.AddComponent(1, 1, Button(gp, '(1,1)'), expand=0, align='c')
        gp.AddComponent(2, 0, Button(gp, '(2,0)'), expand=1)
        gp.Pack()

        self.SetSize((200, 200))

        print gp[2,0]  # should print Button object

# TODO: Add a more realistic example with labels and textboxes and such...

app = Application(MainFrame)
app.Run()
