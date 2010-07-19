# textentrydialog1.py

import sys
sys.path.append("../..")

from wax import *

class MainFrame(Frame):
    def Body(self):
        self.AddComponent(Button(self, "one", event=self.OnClick))
        self.Pack()
    def OnClick(self, event=None):
        dlg = TextEntryDialog(self)
        result = dlg.ShowModal()
        if result == 'ok':
            print dlg.GetValue()
        dlg.Destroy()

app = Application(MainFrame)
app.MainLoop()
