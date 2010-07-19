# messagedialog1.py
# Demonstrate MessageDialog and showdialog.

import sys
sys.path.append("../..")

from wax import *

class MainFrame(Frame):
    def Body(self):
        self.AddComponent(Button(self, "one", event=self.OnClick))
        self.AddComponent(Button(self, "two", event=self.OnClick2))
        self.AddComponent(Button(self, "three", event=self.OnClick3))
        self.Pack()
    def OnClick(self, event=None):
        dlg = MessageDialog(self, title="Holy cow", text="You wanna dance?",
              ok=0, yes_no=1)
        print dlg.ShowModal()
        dlg.Destroy()
    def OnClick2(self, event=None):
        print showdialog(MessageDialog, self, title="Holy smoke",
              text="Did that hurt?", ok=0, yes_no=1)
    def OnClick3(self, event=None):
        print showdialog(MessageDialog, self, text="Resistance is futile.")


app = Application(MainFrame)
app.MainLoop()
