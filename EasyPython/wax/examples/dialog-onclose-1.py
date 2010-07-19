# dialog-onclose-1.py
# Demonstrates/tests Dialog.OnClose.

from wax import *

class MyDialog(Dialog):
    def Body(self):
        indent = ""
        for color in ("blue", "red", "black", "yellow", "peachpuff", "salmon",
                      "purple"):
            label = Label(self, indent + "Obey your Python")
            self.AddComponent(label, border=5)
            label.ForegroundColor = color
            indent = indent + "  "
    def OnClose(self, event):
        print "I'm sorry, but I can't let you do that, Dave."

class MainFrame(Frame):
    def Body(self):
        b = Button(self, "Show 'em my motto!", event=self.ShowDialog)
        self.AddComponent(b, border=10, expand='both')
        self.Pack()
        self.Size = (150, 150)
    def ShowDialog(self, event):
        dlg = MyDialog(self, "Obey your Python!")
        try:
            dlg.ShowModal()
        finally:
            dlg.Destroy()

app = Application(MainFrame, title='dialog-onclose-1')
app.Run()

