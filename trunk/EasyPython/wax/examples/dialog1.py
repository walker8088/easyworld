# dialog1.py

import sys
sys.path.append("../..")

from wax import *

WaxConfig.default_font = ("Verdana", 9)

class MainFrame(Frame):
    def Body(self):
        self.AddComponent(Button(self, "one", event=self.OnClick))
        self.Pack()
    def OnClick(self, event=None):
        # show an empty dialog... ugly, but it should work
        dlg = Dialog(self, "JUst some dialog")
        print dlg.OnCharHook
        print dlg.ShowModal()
        dlg.Destroy()

app = Application(MainFrame)
app.MainLoop()
