# canvas3.py
# Updated for wxPython 2.5.2.7.

from wax import *
from wxPython.wx import *

class MyCanvas(Canvas):

    def Init(self):
        self.SetBackgroundColour('WHITE')

    def OnDraw(self, dc):
        dc.SetTextForeground('BLACK')
        dc.SetPen(wxMEDIUM_GREY_PEN)

        self.DrawHexagons(dc, 300, 10, radius=40, max_number=11)

    def DrawHexagons(self, dc, x, y, radius, max_number):
        for i in range(1, max_number+1):
            offset = i * -0.5 * radius
            for j in range(i):
                self.DrawHexagon(dc, x + offset + j * radius,
                 y + (i * 0.75 * radius), radius)

    def DrawHexagon(self, dc, x, y, radius):
        # does not seem like a 'real' hexagon, but this will do for now
        p1 = (x, y)
        p2 = (x + 0.5 * radius, y + 0.25 * radius)
        p3 = (p2[0], p2[1] + 0.5 * radius)
        p4 = (p1[0], p1[1] + radius)
        p5 = (x - 0.5 * radius, p3[1])
        p6 = (x - 0.5 * radius, y + 0.25 * radius)

        dc.DrawLinePoint(p1, p2)
        dc.DrawLinePoint(p2, p3)
        dc.DrawLinePoint(p3, p4)
        dc.DrawLinePoint(p4, p5)
        dc.DrawLinePoint(p5, p6)
        dc.DrawLinePoint(p6, p1)

class MainFrame(Frame):
    def Body(self):
        canvas = MyCanvas(self)
        self.SetSize((600, 500))

app = Application(MainFrame)
app.MainLoop()
