# simple-1.py

from wax import *

class MainFrame(PlainFrame):
    def Body(self):
        self.Size = 300, 400
        b = Button(self, "Click me", size=(90,24), event=self.OnClickButton)
        self.AddComponent(50, 50, b)

        self.Pack()
        # still necessary for a PlainFrame, although it has a different function
        # here

    def OnClickButton(self, event):
        ShowMessage("sample", "I've been clicked!", icon='information')

app = Application(MainFrame, title="This is a Wax frame")
app.Run()
