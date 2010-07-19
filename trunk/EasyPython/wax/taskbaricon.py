# taskbaricon.py
# Only tested on Windows NT 4, 2000, XP

import waxobject
import wx

class TaskBarIcon(wx.TaskBarIcon, waxobject.WaxObject):

    __events__ = {
        'LeftDoubleClick': wx.EVT_TASKBAR_LEFT_DCLICK,
        'RightUp': wx.EVT_TASKBAR_RIGHT_UP,
    }

    def __init__(self):
        wx.TaskBarIcon.__init__(self)
        self.BindEvents()

    def SetIcon(self, obj, tooltip=""):
        """ Like wx.Frame.SetIcon, but also accepts a path to an icon file. """
        if isinstance(obj, str) or isinstance(obj, unicode):
            obj = wx.Icon(obj, wx.BITMAP_TYPE_ICO)    # FIXME
        wx.TaskBarIcon.SetIcon(self, obj, tooltip)
        # XXX same as Frame.SetIcon... there must be a better way, since I
        # don't like wx.Icon in Wax. :-)

    # XXX more events are in order, of course...

