# properties-parameter-1.py
# Demonstrate 'properties' constructor parameter, and SetAttributes() method
# 2004.07.30 HN

from wax import *

myproperties = {
    'Size': (300, 150),
    'BackgroundColor': 'white',
}

class MainFrame(VerticalFrame):
    def Body(self):
        # Method 1: Set properties through constructor
        p1 = Panel(self, border='sunken', properties=myproperties)
        self.AddComponent(p1, expand="both", border=5)

        # Method 2: Set properties through SetAttributes()
        p2 = Panel(self, border='raised')
        self.AddComponent(p2, expand="both", border=5)
        p2.SetAttributes(**myproperties)
        # Note that SetAttributes can be used to set non-properties as well.

        self.BackgroundColor = p1.BackgroundColor
        self.Pack()

app = Application(MainFrame)
app.Run()
