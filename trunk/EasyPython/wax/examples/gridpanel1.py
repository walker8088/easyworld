# gridpanel1.py

from wax import *

WaxConfig.check_parent = True

class MainFrame(Frame):
    def Body(self):
        gp = GridPanel(self, rows=3, cols=3, hgap=1, vgap=1)
        gp[0,0] = Button(gp, "(0,0)")
        gp.AddComponent(1, 1, Button(gp, "(1,1)"))
        gp.AddComponent(2, 2, TextBox(gp, text="foo\nbar", multiline=1))
        gp.Pack()

        self.SetSize((200, 200))

app = Application(MainFrame)
app.Run()
