# choicedialog1.py

import sys
sys.path.append("../..")

from wax import *
from wax.tools.choicedialog import ChoiceDialog

CHOICES = ['vanilla', 'chocolate', 'mocha', 'strawberry', 'lemon', 'banana',
           'raspberry', 'walnut', 'mint', 'chocolate chip cookie dough']

class MainFrame(Frame):
    def Body(self):
        self.AddComponent(Button(self, "single", event=self.OnClick))
        self.AddComponent(Button(self, "multiple", event=self.OnClick))
        self.Pack()
    def OnClick(self, event=None):
        obj = event.GetEventObject()
        selection = obj.GetLabel()
        dlg = ChoiceDialog(self, choices=CHOICES, selection=selection)
        if dlg.ShowModal() == 'ok':
            if selection == 'single':
                print dlg.choice, CHOICES[dlg.choice]
            else:
                print dlg.choice,
                print [CHOICES[x] for x in dlg.choice]
        dlg.Destroy()

app = Application(MainFrame)
app.MainLoop()
