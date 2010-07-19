# radiobutton.py

import wx
import waxobject
import styles

class RadioButton(wx.RadioButton, waxobject.WaxObject):

    __events__ = {
        'Select': wx.EVT_RADIOBUTTON,
    }

    def __init__(self, parent, text='', size=None, **kwargs):
        style = 0
        style |= self._params(kwargs)
        style |= styles.window(kwargs)

        wx.RadioButton.__init__(self, parent, wx.NewId(), text,
         size=size or (-1,-1), style=style)

        self.SetDefaultFont()
        styles.properties(self, kwargs)

    #
    # style parameters

    def _params(self, kwargs):
        flags = 0
        flags |= styles.stylebool('start_group', wx.RB_GROUP, kwargs)
        flags |= styles.stylebool('single', wx.RB_SINGLE, kwargs)
        return flags

