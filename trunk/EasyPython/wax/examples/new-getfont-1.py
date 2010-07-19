# new-getfont-1.py
# Widgets that derive from WaxObject now have a GetFont() that returns a Wax
# Font, rather than a wx.Font.

from wax import *

class MainFrame(Frame):
    def Body(self):
        b = Button(self, "a button", event=self.OnButtonClick)
        self.AddComponent(b, expand='both')
        self.Pack()
        self.Size = (100, 100)
    def OnButtonClick(self, event):
        button = event.GetEventObject()
        font = button.GetFont()
        print font
        print font.IsItalic # does not exist in wx.Font

app = Application(MainFrame)
app.Run()
