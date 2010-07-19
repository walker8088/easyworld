# groupbox.py

# todo: styles

import wx
import containers

class GroupBox(wx.Panel, containers.GroupBoxContainer):

    def __init__(self, parent, text='', direction='v'):
        wx.Panel.__init__(self, parent, wx.NewId())
        self.staticbox = wx.StaticBox(self, wx.NewId(), text)
        self._create_sizer(self.staticbox, direction)

        self.SetDefaultFont()
        self.Body()

