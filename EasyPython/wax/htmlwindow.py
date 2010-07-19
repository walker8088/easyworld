# htmlwindow.py

# todo: styles

import wx.html
import waxobject

class HTMLWindow(wx.html.HtmlWindow, waxobject.WaxObject):

    def __init__(self, parent, fullrepaint=1):
        style = 0
        if not fullrepaint:
            style |= wx.NO_FULL_REPAINT_ON_RESIZE
        wx.html.HtmlWindow.__init__(self, parent, wx.NewId(), style=style)

