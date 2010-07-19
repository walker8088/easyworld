# gauge.py

from wax import waxobject, core, styles
import wx

class Gauge(wx.Gauge, waxobject.WaxObject):

    __events__ = { }

    def __init__(self, parent, range=100, size=None, **kwargs):
        style = 0
        style |= self._params(kwargs)
        style |= styles.window(kwargs)
        
        wx.Gauge.__init__(self, parent, wx.NewId(), range, size=size or (250,-1), style=style)
        self.SetDefaultFont()
        self.SetRange(range)
        
        self.BindEvents()
        styles.properties(self, kwargs)

    #
    # style parameters
    
    __styles__ = {
        'orientation': ({
            "horizontal": wx.GA_HORIZONTAL,
            "vertical": wx.GA_VERTICAL,
        }, styles.DICTSTART),
        'smooth': (wx.GA_SMOOTH, styles.NORMAL),
    }
