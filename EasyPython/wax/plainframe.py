# plainframe.py

# todo: styles

import wx
import containers

class PlainFrame(wx.Frame, containers.PlainContainer):

    __events__ = {
        'Close': wx.EVT_CLOSE,
        'Iconize': wx.EVT_ICONIZE,
        'Show': wx.EVT_SHOW,
        'Activate': wx.EVT_ACTIVATE,
        'Idle': wx.EVT_IDLE,
        # some of these might be better off in events.py
    }

    def __init__(self, parent=None, title="", wants_chars=0, tab_traversal=0):
        style = wx.DEFAULT_FRAME_STYLE
        if wants_chars:
            style |= wx.WANTS_CHARS
        if tab_traversal:
            style |= wx.TAB_TRAVERSAL
        wx.Frame.__init__(self, parent, wx.NewId(), title, style=style)

        self._create_sizer()
        self.BindEvents()
        self.SetDefaultFont()
        self.Body()

    def SetIcon(self, obj):
        """ Like wx.Frame.SetIcon, but also accepts a path to an icon file. """
        if isinstance(obj, str) or isinstance(obj, unicode):
            obj = wx.Icon(obj, wx.BITMAP_TYPE_ICO)    # FIXME
        wx.Frame.SetIcon(self, obj)


# XXX There's duplication here with Frame...
