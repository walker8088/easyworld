# gridframe.py

# todo: styles

import wx
import containers
import frame

class GridFrame(wx.Frame, containers.GridContainer):
    """ Top-level frame (window) with built-in sizer. """

    def __init__(self, parent=None, title="", wants_chars=0, rows=3, cols=3,
     hgap=1, vgap=1):
        style = wx.DEFAULT_FRAME_STYLE
        if wants_chars:
            style |= wx.WANTS_CHARS
        if tab_traversal:
            style |= wx.TAB_TRAVERSAL
        wx.Frame.__init__(self, parent, wx.NewId(), title, style=style)

        self._create_sizer(rows, cols, hgap, vgap)
        self.SetDefaultFont()
        self.Body()

    def SetIcon(self, obj):
        """ Like wx.Frame.SetIcon, but also accepts a path to an icon file. """
        if isinstance(obj, str) or isinstance(obj, unicode):
            obj = wx.Icon(obj, wx.BITMAP_TYPE_ICO)    # FIXME
        wx.Frame.SetIcon(self, obj)

# XXX There's duplicate code in Frame and GridFrame.  >=(
# Put in a mixin?

