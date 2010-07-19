# mdiframes.py

# todo: styles

import wx
import containers

class MDIChildFrame(wx.MDIChildFrame, containers.Container):
    """ MDI Child frame (window) with built-in sizer. """

    def __init__(self, parent=None, title="", direction="H", wants_chars=0):
        wx.MDIChildFrame.__init__(self, parent, wx.NewId(), title, style=wx.DEFAULT_FRAME_STYLE)
        if wants_chars:
            self.SetWindowStyleFlag(self.GetWindowStyleFlag() | wx.WANTS_CHARS)

        self._create_sizer(direction)
        self.SetDefaultFont()
        self.Body()

    def SetIcon(self, obj):
        """ Like wx.Frame.SetIcon, but also accepts a path to an icon file. """
        if isinstance(obj, str) or isinstance(obj, unicode):
            obj = wx.Icon(obj, wx.BITMAP_TYPE_ICO)    # FIXME
        wx.Frame.SetIcon(self, obj)


class MDIParentFrame(wx.MDIParentFrame, containers.Container):
    """ MDI main frame (window)"""

    def __init__(self, parent=None, title=""):
        wx.MDIParentFrame.__init__(self, parent, wx.NewId(), title,
         style=wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE)
        self._create_sizer('H')
        self.SetDefaultFont()
        self.Body()
        self.menubar = wx.MenuBar()

    def SetIcon(self, obj):
        """ Like wx.Frame.SetIcon, but also accepts a path to an icon file. """
        if isinstance(obj, str) or isinstance(obj, unicode):
            obj = wx.Icon(obj, wx.BITMAP_TYPE_ICO)    # FIXME
        wx.Frame.SetIcon(self, obj)
