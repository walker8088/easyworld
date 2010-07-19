# slider.py

from wax import waxobject, core, styles
import wx

class Slider(wx.Slider, waxobject.WaxObject):

    __events__ = {
        'Scroll': wx.EVT_SCROLL,
    }

    def __init__(self, parent, tickfreq=5, min=0, max=100, event=None, size=None, **kwargs):
        style = 0
        style |= self._params(kwargs)
        style |= styles.window(kwargs)
        
        wx.Slider.__init__(self, parent, wx.NewId(), size=size or (-1,-1), style=style)
        self.SetDefaultFont()
        self.SetTickFreq(tickfreq)
        self.SetRange(min, max)
        
        self.BindEvents()
        if event:
            self.OnScroll = event
        styles.properties(self, kwargs)

    #
    # style parameters
    
    __styles__ = {
        'labels': (wx.SL_LABELS, styles.NORMAL),
        'ticks': ({
            "left": wx.SL_LEFT | wx.SL_AUTOTICKS,
            "right": wx.SL_RIGHT | wx.SL_AUTOTICKS,
            "top": wx.SL_TOP | wx.SL_AUTOTICKS,
            "bottom": wx.SL_BOTTOM | wx.SL_AUTOTICKS,
        }, styles.DICTSTART),
        'orientation': ({
            "horizontal": wx.SL_HORIZONTAL,
            "vertical": wx.SL_VERTICAL,
        }, styles.DICTSTART),
    }

