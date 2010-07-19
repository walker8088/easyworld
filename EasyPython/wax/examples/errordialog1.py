# errordialog1.py

import sys
sys.path.append("../..")

from wax import *
from wax.tools.errordialog import ErrorDialog

class MainFrame(Frame):
    def Body(self):
        self.AddComponent(Button(self, "one", event=self.OnClick))
        self.Pack()
    def OnClick(self, event=None):
        try:
            x = 1/0
        except:
            dlg = ErrorDialog(self, *sys.exc_info())
            print dlg.ShowModal()
            dlg.Destroy()

app = Application(MainFrame)
app.MainLoop()
