# checkbox-2.py
# Demonstrates 'align' option, and 3-state checkboxen.

from wax import *
import wx

class MainFrame(VerticalFrame):
    def Body(self):
        cb1 = CheckBox(self, "aligned to left")
        self.AddComponent(cb1, expand='h', border=5)
        cb2 = CheckBox(self, "aligned to right", align='r')
        self.AddComponent(cb2, expand='h', border=5)

        for s in ('checked', 'unchecked', 'undetermined'):
            cbx = CheckBox(self, "3-state " + s, states=3)
            self.AddComponent(cbx, expand='h', border=5)
            cbx.Set3StateValue(s)

        self.Pack()
        self.Size = (200, 200)

app = Application(MainFrame, title='checkbox-2.py')
app.Run()
