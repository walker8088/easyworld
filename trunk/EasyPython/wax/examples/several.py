# several.py

import sys
sys.path.append("../..")
from wax import *


class MainFrame(Frame):

    def Body(self):
        self.SetSize((300,200))
        b = Button(self, "a button")
        self.AddComponent(b, align='center', expand='h', border=2)

        l = Label(self, "a label")
        self.AddComponent(l, align='center', border=2)

        t = TextBox(self, "some text")
        self.AddComponent(t, align='center', expand='h', border=2)

        cb = ComboBox(self, ["one", "two", "three"])
        self.AddComponent(cb, align='center', expand='h', border=2)

        lb = ListBox(self, ["hava", "nagila", "hava"])
        self.AddComponent(lb, expand='h', border=1)

        self.Pack()

app = Application(MainFrame, title="Just some stuff", direction='vertical')
app.MainLoop()
