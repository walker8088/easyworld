# timer.py

import wx
import waxobject

class Timer(wx.Timer, waxobject.WaxObject):

    def __init__(self, obj, event=None):
        id = wx.NewId()
        wx.Timer.__init__(self, obj, id)

        if event:
            self.OnTimer = event

        wx.EVT_TIMER(obj, id, self._OnTimer)
        # this is a special case that cannot be handled easily with the
        # current WaxObject event mechanism

    def _OnTimer(self, event): self.OnTimer(event)
    def OnTimer(self, event): event.Skip()

    # the obvious methods apply:
    # Start(interval, oneshot=False)
    # Stop()

