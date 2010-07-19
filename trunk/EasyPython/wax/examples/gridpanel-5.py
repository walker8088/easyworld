# gridpanel-5.py

from wax import *

class MainFrame(Frame):
    def Body(self):
        gp = GridPanel(self, rows=3, cols=3, hgap=0, vgap=0)
        gp.AddComponent(0, 0, Button(gp, "(0, 0)"), expand=1)
        gp.AddComponent(1, 0, Button(gp, "(1, 0)"), expand=1)
        gp.AddComponent(2, 0, Button(gp, "(2, 0)"), expand=1)
        gp.AddComponent(0, 1, Button(gp, "(0, 1)"), expand=1)
        gp.AddComponent(0, 2, Button(gp, "(0, 2)"), expand=1)

        yellow_button = Button(gp, "(1, 1)", BackgroundColor='yellow')
        gp.AddComponent(1, 1, yellow_button, border=10, align='th', expand=0)

        gp.Pack()

        self.AddComponent(gp, expand='both')
        self.Pack()
        # set the size so the alignment of the yellow button shows, together
        # with the border
        self.Size = 300, 300

app = Application(MainFrame)
app.Run()
