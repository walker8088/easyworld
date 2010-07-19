# simpleeditor.py

import image
import waxobject
import wx
from wx.lib.editor import Editor

class SimpleEditor(Editor, waxobject.WaxObject):

    def __init__(self, parent):
        # for some reason, this editor uses PNG files for cursor and EOF >_<
        image.AddImageHandler('png')

        Editor.__init__(self, parent, wx.NewId(), style=wx.SUNKEN_BORDER)
