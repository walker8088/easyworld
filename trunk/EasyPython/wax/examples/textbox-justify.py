# textbox-justify.py
# Q: Why doesn't Tab work here?

from wax import *

class MainFrame(VerticalFrame):
    def Body(self):
        for j in ("left", "center", "right"):
            t = TextBox(self, multiline=0, text=j, justify=j)
            t.SizeX = 200
            self.AddComponent(t, expand='h', border=5)
        self.Pack()

app = Application(MainFrame, title='textbox-justify')
app.Run()
