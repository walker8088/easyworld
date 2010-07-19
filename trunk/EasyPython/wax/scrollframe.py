# scrollframe.py

import wx
import waxobject, containers
import styles

class ScrollFrame(wx.ScrolledWindow, containers.Container):

    __events__ = {
        'Paint': wx.EVT_PAINT,
    }

    def __init__(self, parent, direction='v', **kwargs):
        style = 0
        style |= styles.window(kwargs)
        
        wx.ScrolledWindow.__init__(self, parent, wx.NewId(), style=style)

        self.BindEvents()
        self._create_sizer(direction)
        styles.properties(self, kwargs)
        self.Body()

    def OnPaint(self, event):
        # override this to draw on the canvas
        event.Skip()
        # this is necessary, otherwise the event will stop the program from
        # being exited the normal way, among other things.
        