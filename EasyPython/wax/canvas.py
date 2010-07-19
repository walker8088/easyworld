# canvas.py

import wx
import waxobject

class Canvas(wx.ScrolledWindow, waxobject.WaxObject):

    __events__ = {
        'Paint': wx.EVT_PAINT,
    }

    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, wx.NewId())
        self.Init()

        self.BindEvents()

    def _OnPaint(self, event=None):
        self.OnPaint(event)
    def OnPaint(self, event=None):
        dc = wx.PaintDC(self)
        self.PrepareDC(dc)
        self.OnDraw(dc)
        event.Skip()

    def OnDraw(self, dc):
        # override to draw on the canvas
        pass

    def Init(self):
        # override to place scrollbars, set color, etc.
        pass

