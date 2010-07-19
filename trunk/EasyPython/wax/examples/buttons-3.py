# buttons-3.py
# Demonstrate Button styles.

from wax import *

ALIGNMENTS = ("left", "right", "bottom", "top")

class MainFrame(HorizontalFrame):
    def Body(self):
        for alignment in ALIGNMENTS:
            b = Button(self, text=alignment, align=alignment)
            self.AddComponent(b, expand="both")
        self.AddComponent(Button(self, text='exact', exactfit=1))
        self.Pack()

app = Application(MainFrame)
app.Run()
