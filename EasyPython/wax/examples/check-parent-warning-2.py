# check-parent-warning-2.py

from wax import *

WaxConfig.check_parent = True
# causes a warning to be displayed for wrong parent-container relationships

class MainFrame(Frame):
    def Body(self):
        p = Panel(self)
        b = Button(self, "Wrong") # wrong parent; should be p
        p.AddComponent(b, expand='both')

        p.Pack()
        self.AddComponent(p, expand='both')

        self.Pack()


app = Application(MainFrame)
app.Run()
