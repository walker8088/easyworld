# findreplacedialog1.py
# Demonstrates FindReplaceDialog, and how it ties in with TextBox and
# StyledTextBox.

from wax import *

class MainFrame(Frame):

    def Body(self):
        b = Button(self, "Find dialog", event=self.ShowFindDialog)
        self.AddComponent(b, stretch=1)
        b = Button(self, "Find/Replace dialog", event=self.ShowReplaceDialog)
        self.AddComponent(b, stretch=1)
        self.tb = TextBox(self, multiline=1, size=(300, 150))
        self.tb.OnGetFocus = self.tb_OnGetFocus
        self.AddComponent(self.tb, expand='both')
        self.stb = StyledTextBox(self, size=(300, 150))
        self.stb.OnGetFocus = self.stb_OnGetFocus
        self.AddComponent(self.stb, expand='both')
        self.Pack()

        self.c = self.tb
    def ShowFindDialog(self, event=None):
        dlg = FindReplaceDialog(self, self.c)
        dlg.Show()  # not ShowModal

    def ShowReplaceDialog(self, event=None):
        dlg = FindReplaceDialog(self, self.c, replace=1)
        dlg.Show()  # not ShowModal

    def tb_OnGetFocus(self, event=None):
        self.c = self.tb
        event.Skip()

    def stb_OnGetFocus(self, event=None):
        self.c = self.stb
        event.Skip()


app = Application(MainFrame, title='Find/Replace Test', direction='vertical')
app.Run()
