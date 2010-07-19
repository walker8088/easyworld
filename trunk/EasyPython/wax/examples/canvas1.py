# canvas1.py
# Updated for wxPython 2.5.2.7.

from wax import *
from wxPython.wx import *

class MyCanvas(Canvas):
    def Init(self):
        self.SetBackgroundColour('WHITE')
        self.SetScrollbars(20, 20, 100, 100)
        self.bitmap = Image('heretic2.ico').ConvertToBitmap()
    def OnDraw(self, dc):
        dc.SetTextForeground('BLUE')
        dc.SetPen(wxMEDIUM_GREY_PEN)
        for i in range(100):
            dc.DrawLine(0, i*10, i*10, 0)

        dc.DrawBitmap(self.bitmap, 50, 50, 1)

class MainFrame(Frame):
    def Body(self):
        canvas = MyCanvas(self)

app = Application(MainFrame)
app.MainLoop()
