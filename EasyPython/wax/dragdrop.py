# dragdrop.py

import wx

# These can be overridden if you need them:
# def OnDropFiles(self, x, y, files)
# def OnDragOver(self, x, y, d)
# def OnEnter(self, x, y, d)
# def OnLeave(self, d)
#
# However, for most purposes, it will probably suffice to pass in a function
# to <event>.

class FileDropTarget(wx.FileDropTarget):
    # note that you can pass an event, or just override OnDropFiles.

    def __init__(self, window, event=None):
        wx.FileDropTarget.__init__(self)
        self.window = window
        self.event = event
        self.window.SetDropTarget(self)

    def OnDropFiles(self, x, y, filenames):
        if self.event:
            self.event(x, y, filenames)

class TextDropTarget(wx.TextDropTarget):

    def __init__(self, window, event=None):
        wx.TextDropTarget.__init__(self)
        self.window = window
        self.event = event
        self.window.SetDropTarget(self)

    def OnDropText(self, x, y, text):
        if self.event:
            self.event(x, y, text)

    def OnDragOver(self, x, y, d):
        return wx.DragCopy
        # XXX not sure what this does; copied from wxPython demo

class URLDropTarget(wx.PyDropTarget):
    
    def __init__(self, window, event=None):
        # <event> is a function with signature (x, y, d, url).
        wx.PyDropTarget.__init__(self)
        self.window = window
        self.event = event
        self.window.SetDropTarget(self)
        self.data = wx.URLDataObject()
        self.SetDataObject(self.data)
        
    def OnDragOver(self, x, y, d):
        return wx.DragLink
        
    def OnData(self, x, y, d):
        if not self.GetData():
            return wx.DragNone
        url = self.data.GetURL()
        if self.event:
            self.event(x, y, d, url)
        return d
