# styledtextbox1.py

from wax import *

class MainFrame(Frame):
    def Body(self):
        b = Button(self, "dummy")
        self.AddComponent(b, expand='h')
        stb = StyledTextBox(self, size=(400,300))
        self.AddComponent(stb, expand='both')
        self.Pack()

#)

app = Application(MainFrame, title="StyledTextBox demo", direction='v')
app.Run()
