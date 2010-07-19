# sound.py

import wx
import waxobject

class Sound(wx.Sound, waxobject.WaxObject):

    def Play(self, sync=1):
        mode = wx.SOUND_SYNC
        if not sync:
            mode = wx.SOUND_ASYNC
        wx.Sound.Play(self, mode)



