# buttons-3a.py
# Demonstrate Button styles using new and improved SetWindowStyle.

from wax import *

ALIGNMENTS = ("left", "right", "bottom", "top")

class MainFrame(HorizontalFrame):
    def Body(self):
        for alignment in ALIGNMENTS:
            b = Button(self, text=alignment)
            self.AddComponent(b, expand="both")

            # set styles *after* creating the Button:
            b.SetWindowStyle(align=alignment)

        self.AddComponent(Button(self, text='exact', exactfit=1))
        self.Pack()

app = Application(MainFrame)
app.Run()
