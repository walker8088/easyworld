# messagedialog2.py

from wax import *

class MainFrame(Frame):

    def Body(self):
        choices = MessageDialog._icons.keys()
        choices.sort()

        self.dd = DropDownBox(self, choices)
        self.AddComponent(self.dd, border=10)

        b = Button(self, "Show message", self.ShowMessage)
        self.AddComponent(b, border=10)

        self.Pack()
        self.SetSize((200, 200))    # so the window doesn't look so wimpy :)

    def ShowMessage(self, event):
        choice = self.dd.GetStringSelection()
        dlg = MessageDialog(self, "A message", "You chose: " + repr(choice),
              icon=choice)
        dlg.ShowModal()
        dlg.Destroy()

if __name__ == "__main__":

    app = Application(MainFrame, direction='v')
    app.Run()

