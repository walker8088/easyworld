# shell1.py

import sys; sys.path.insert(0, "../..")
from wax import *

class MainFrame(Frame):
    def Body(self):
        nb = NoteBook(self)
        self.AddComponent(nb)

        nb.AddPage(PyCrust(nb), "PyCrust")
        nb.AddPage(PyCrustFilling(nb), "PyCrustFilling")
        self.Pack()

app = Application(MainFrame, title="PyCrust demo")
app.Run()
