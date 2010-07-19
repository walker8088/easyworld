# togglebutton.py

# todo: styles, if possible (like a regular Button)

import containers
import waxobject
import wx

class ToggleButton(wx.ToggleButton, waxobject.WaxObject):

    __events__ = {
        'Click': wx.EVT_TOGGLEBUTTON,
        'Toggle': wx.EVT_TOGGLEBUTTON,  # use one or the other
    }

    def __init__(self, parent, text="", event=None, size=None):
        assert isinstance(parent, containers.Container)
        wx.ToggleButton.__init__(self, parent, wx.NewId(), text)
        self.SetDefaultFont()
        self.BindEvents()
        if event:
            self.OnClick = event
        if size:
            self.SetSize(size)

    def Pressed(self):  # alias
        return self.GetValue()

