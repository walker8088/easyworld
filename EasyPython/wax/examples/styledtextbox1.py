# styledtextbox1.py

from wax import *

class MainFrame(Frame):
    def Body(self):
        stb = StyledTextBox(self, size=(400,300))
        self.AddComponent(stb)
        self.Pack()

#)

app = Application(MainFrame, title="StyledTextBox demo")
app.Run()
