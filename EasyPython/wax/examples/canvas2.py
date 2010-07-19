# canvas2.py
# A clumsy way of moving a "sprite" around, but it's gonna have to do...

from wax import *
from wxPython.wx import *

class Sprite:
    def __init__(self, bitmap):
        self.bitmap = bitmap
        self.background = None
        self.x = self.y = 0
    def Draw(self, dc):
        # copy background from dc to memory object
        memdc = wxMemoryDC()
        memdc.Blit(0, 0, self.bitmap.GetWidth(), self.bitmap.GetHeight(), dc,
                   self.x, self.y, wxCOPY, 1)
        self.background = memdc # keep around for later

        dc.DrawBitmap(self.bitmap, self.x, self.y, 1)
    def Hide(self, dc):
        print 'Hiding...'
        dc.Blit(self.x, self.y, self.bitmap.GetWidth(), self.bitmap.GetHeight(),
                self.background, 0, 0, wxCOPY, 0)
        print self.background
    def Move(self, dc, dx, dy):
        self.Hide(dc)
        self.x += dx
        self.y += dy
        self.Draw(dc)

class MyCanvas(Canvas):
    def Init(self):
        self.SetBackgroundColour('WHITE')
        self.SetScrollbars(20, 20, 100, 100)
        self.bitmap = Image('heretic2.ico').ConvertToBitmap()
        self.sprite = Sprite(self.bitmap)
        self.sprite.x = self.sprite.y = 50
    def OnDraw(self, dc):
        dc.SetTextForeground('BLUE')
        dc.SetPen(wxMEDIUM_GREY_PEN)
        for i in range(50):
            dc.DrawLine(0, i*10, i*10, 0)

        self.sprite.Draw(dc)

class MainFrame(Frame):
    def Body(self):
        buttonpanel = Panel(self, direction='horizontal')
        buttonpanel.AddComponent(Button(buttonpanel, "left", event=self.Left))
        buttonpanel.AddComponent(Button(buttonpanel, "right", event=self.Right))
        buttonpanel.Pack()
        self.AddComponent(buttonpanel, stretch=1)

        self.canvas = MyCanvas(self)
        self.canvas.SetSize((400,300))
        self.AddComponent(self.canvas, expand=1, stretch=1)

        self.Pack()

    def Left(self, event=None):
        dc = wxClientDC(self.canvas)
        self.canvas.sprite.Move(dc, -10,0)
        self.canvas.Refresh()

    def Right(self, event=None):
        dc = wxClientDC(self.canvas)
        self.canvas.sprite.Move(dc, 10,0)
        self.canvas.Refresh()

app = Application(MainFrame, direction='vertical')
app.MainLoop()
