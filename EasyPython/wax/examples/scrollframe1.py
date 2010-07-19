# scrollframe1.py
# Adapted for wxPython 2.5.1.5.

from wax import *
import wx

class MyScrollFrame(ScrollFrame):

    def OnPaint(self, event=None):
        self.bitmap = Image('heretic2.ico').ConvertToBitmap()
        dc = wx.PaintDC(self)
        self.PrepareDC(dc)
        self.DoDrawing(dc)

        event.Skip()

    def DoDrawing(self, dc):
        dc.SetTextForeground('BLUE')
        dc.SetPen(wx.MEDIUM_GREY_PEN)
        for i in range(100):
            dc.DrawLine(0, i*10, i*10, 0)

        dc.DrawBitmap(self.bitmap, 50, 50, 1)

class MainFrame(Frame):
    def Body(self):
        scrollframe = MyScrollFrame(self)
        scrollframe.SetBackgroundColour("WHITE")
        scrollframe.SetScrollbars(20, 20, 100, 100)

app = Application(MainFrame)
app.MainLoop()
