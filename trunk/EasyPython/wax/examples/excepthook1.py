# excepthook1.py#
#
# If the root frame contains a method __ExceptHook__, then this is automagically
# set as the exception hook for/by the Application.
#
# (If you want to remove or replace it, you can always tinker around with
# sys.excepthook.)

import sys
sys.path.append("../..")

from wax import *
from wax.tools.errordialog import ErrorDialog

class MainFrame(Frame):
    def Body(self):
        self.AddComponent(Button(self, "one", event=self.OnClick))
        self.Pack()
    def OnClick(self, event=None):
        # deliberately create an error
        x = 1/0
    def __ExceptHook__(self, exctype, value, traceback):
        dlg = ErrorDialog(self, exctype, value, traceback)
        dlg.ShowModal()
        dlg.Destroy()

app = Application(MainFrame)
app.MainLoop()
