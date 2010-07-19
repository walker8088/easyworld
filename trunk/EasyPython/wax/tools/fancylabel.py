#-----------------------------------------------------------------------
# Name:     fancylabel.py, wax.FancyLabel
# Author:   Jason Gedge
# Purpose:  A control for rendering XML specified text
# TODO:
#   - Ensure that when text is changed that self.extent is updated
#-----------------------------------------------------------------------


import wx
import wx.lib.fancytext as fancytext
from wax import containers
from wax import waxobject
from wax import styles

class FancyLabel(wx.PyWindow, waxobject.WaxObject):
    """A control for rendering XML specified text."""

    __events__ = {
        'Paint': wx.EVT_PAINT,
        'EraseBackground': wx.EVT_ERASE_BACKGROUND,
    }

    def __init__(self, parent, text='', pos=wx.DefaultPosition,
                 size=wx.DefaultSize, **kwargs):
        
        assert isinstance(parent, containers.Container)
        
        style = 0
        style |= self._params(kwargs)
        style |= styles.window(kwargs)
        
        wx.PyWindow.__init__(self, parent, wx.NewId(), pos, size, style, "fancylabel")
        
        self.bg = wx.Brush( wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE) )
        self.SetText(text)
        self.SetDefaultFont()
        self.BindEvents()
        
        styles.properties(self, kwargs)

    def OnEraseBackground(self, event):
        pass

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC( self )
        dc.SetBackground(self.bg)
        dc.Clear()
        fancytext.RenderToDC(self.text, dc, 1, 1)
        event.Skip()

    def _UpdateTextSize(self):
        dc = wx.ClientDC(self)
        w, h = fancytext.GetExtent(self.text, dc)
        self.extent = (w + 5, h) # looks better with this
        if not self.noresize:
            self.SetSize(self.extent)

    def SetText(self, text):
        self.text = text
        self._UpdateTextSize()

    def GetText(self):
        return self.text

    #
    # style parameters
    
    #_label_align = {
    #    'left': wx.ALIGN_LEFT,
    #    'right': wx.ALIGN_RIGHT,
    #    'center': wx.ALIGN_CENTRE,
    #    'centre': wx.ALIGN_CENTRE,
    #}

    def _params(self, kwargs):
        flags = 0
        #flags |= styles.styledictstart('align', self._label_align, kwargs, wx.ALIGN_LEFT)
        
        # Should this be here?
        self.noresize = styles.stylebool('noresize', True, kwargs)
        
        return flags
