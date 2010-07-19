# checklistbox.py
# XXX doesn't work on Mac.

# todo: styles (if any)

import wx
import waxobject
import styles

class CheckListBox(wx.CheckListBox, waxobject.WaxObject):

    __events__ = {
        'CheckListBox': wx.EVT_CHECKLISTBOX,
    }

    def __init__(self, parent, choices=[], size=None, **kwargs):
        style = 0
        #style |= checklistbox_params(kwargs)
        style |= styles.window(kwargs)

        wx.CheckListBox.__init__(self, parent, wx.NewId(), choices=choices, style=style)

        self.SetDefaultFont()
        self.BindEvents()

        styles.properties(self, kwargs)


