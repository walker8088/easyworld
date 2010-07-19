# layout-1.py

from wax import *

class MainFrame(Frame):
    def Body(self):
        b = Button(self, "stretch")
        self.AddComponent(b, stretch=1, border=1)

        b = Button(self, "expand")
        self.AddComponent(b, expand=1, border=1)

        b = Button(self, "stretch && expand")
        self.AddComponent(b, stretch=1, expand=1, border=1)

        self.Pack()

app = Application(MainFrame, direction='v')
app.Run()
