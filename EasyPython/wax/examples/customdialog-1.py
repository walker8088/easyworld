# customdialog-1.py

from wax import *

class MyDialog(CustomDialog):
    def Body(self):
        label = Label(self, "There are unsaved data.\nWhat do you want to do?")
        self.AddComponent(label, border=10, expand='h')
        self.AddSpace(10)
        b1 = Button(self, "Save")
        self.AddComponent(b1, border=3, align='c')
        b2 = Button(self, "Don't save")
        self.AddComponent(b2, border=3, align='c')
        b3 = Button(self, "Cancel")
        self.AddComponent(b3, border=3, align='c')
        b4 = Button(self, "Non-modal button", event=self.OnClickNormal)
        self.AddComponent(b4, border=3, align='c')
        self.AddSpace(10)

        self.SetBehavior(b1, "save", event=self.OnClickSave)
        self.SetBehavior(b2, "dontsave")
        self.SetBehavior(b3, "cancel")

    def OnClickSave(self, event):
        print "You clicked Save!"

    def OnClickNormal(self, event):
        print "I am just a normal button that doesn't harm anybody."

class MainFrame(Frame):
    def Body(self):
        b = Button(self, "Open custom dialog", event=self.OnShowDialog)
        self.AddComponent(b, expand='both', border=10)
        self.Pack()
        self.Size = 150,150
    def OnShowDialog(self, event):
        dlg = MyDialog(self, "Pick your poison")
        result = dlg.ShowModal()
        print "Result returned by CustomDialog:", result
        dlg.Destroy()

app = Application(MainFrame, title="customdialog-1")
app.Run()
