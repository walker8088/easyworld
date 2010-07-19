# expand-parameters-1.py

from wax import *

class MainFrame(VerticalFrame):
    def Body(self):
        b1 = Button(self, "expands horizontally")
        self.AddComponent(b1, expand='h')
        b2 = Button(self, "expands vertically")
        self.AddComponent(b2, expand='v')
        b3 = Button(self, "expands in both ways")
        self.AddComponent(b3, expand='b')
        b4 = Button(self, "does not expand")
        self.AddComponent(b4)

        self.Pack()

app = Application(MainFrame, title='expand-parameters-1')
app.Run()
