# plainpanel.py

# todo: styles

import wx
import containers

class PlainPanel(wx.Panel, containers.PlainContainer):
    """ Sub-level containers inside a frame, used for layout. """
    def __init__(self, parent=None):
        wx.Panel.__init__(self, parent, wx.NewId())

        self._create_sizer()
        self.BindEvents()
        self.SetDefaultFont()
        self.Body()

