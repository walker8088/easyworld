# nopack-1.py

from wax import *

class MainFrame(Frame):
    def Body(self):
        b = Button(self, "poing")
        self.AddComponent(b)
        # make window big so you see the effect
        self.Size = 400, 400

app = Application(MainFrame)
app.Run()
